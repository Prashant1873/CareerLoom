import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from backend.app.db.database import (
    get_targets,
    purge_stale_jobs,
    reconcile_target_jobs,
    upsert_jobs,
)
from backend.app.models.target import CareerTarget, CareerTargetFilterParams
from backend.app.services.sync import JobSyncService

logger = logging.getLogger("careerloom.batch_runner")


@dataclass
class BatchScrapeResult:
    """
    Structured outcome telemetry for a batch scraping run.
    """
    total_targets: int = 0
    successful_targets: int = 0
    failed_targets: int = 0
    live_jobs_found: int = 0
    new_jobs_upserted: int = 0
    archived_jobs_count: int = 0
    purged_jobs_count: int = 0
    elapsed_seconds: float = 0.0
    throughput_jobs_per_sec: float = 0.0
    target_details: List[Dict[str, Any]] = field(default_factory=list)


class BatchScrapeRunner:
    """
    High-throughput async batch scraper executing concurrent ingestion across
    registered CareerTarget records with bounded semaphore concurrency, per-host
    politeness jitter, and strict per-target error isolation.
    """

    def __init__(
        self,
        concurrency: int = 15,
        default_jitter_range: Tuple[float, float] = (0.1, 0.3),
        sync_service: Optional[JobSyncService] = None,
    ):
        self.concurrency = max(1, concurrency)
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.jitter_range = default_jitter_range
        self.sync_service = sync_service or JobSyncService()
        self._last_host_time: Dict[str, float] = {}
        self._host_lock = asyncio.Lock()

    def _extract_host_key(self, target: CareerTarget) -> str:
        """
        Derives ATS domain host key to throttle requests hitting identical upstream infrastructure.
        """
        ats = (target.ats_type or "").strip().lower()
        if ats in ("greenhouse", "lever", "ashby", "smartrecruiters", "workday"):
            return ats

        url = target.feed_url or target.career_url or ""
        if url:
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    return parsed.netloc.lower()
            except Exception:
                pass
        return "custom"

    async def _apply_host_jitter(self, host_key: str) -> None:
        """
        Applies a polite random delay if the same ATS provider was requested recently (T-14-03).
        """
        now = time.time()
        delay = 0.0
        async with self._host_lock:
            last_time = self._last_host_time.get(host_key, 0.0)
            elapsed = now - last_time
            min_gap = 0.2
            if elapsed < min_gap:
                delay = random.uniform(*self.jitter_range)
            self._last_host_time[host_key] = now + delay

        if delay > 0:
            await asyncio.sleep(delay)

    async def scrape_target(
        self,
        target: CareerTarget,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Scrapes a single CareerTarget in complete isolation.
        Errors are caught and logged, never aborting the batch.
        """
        host_key = self._extract_host_key(target)
        await self._apply_host_jitter(host_key)

        fetch_success = False
        error_msg = None
        jobs = []

        async with self.semaphore:
            connector = self.sync_service.connectors.get(target.ats_type.lower())
            try:
                if connector:
                    jobs = await connector.fetch_jobs(
                        company_name=target.name,
                        company_slug=target.slug,
                        domain=target.domain,
                    )
                    fetch_success = True
                elif target.career_url:
                    jobs = await self.sync_service.portal_extractor.scrape_portal(
                        target.career_url, target.name, default_domain=target.domain
                    )
                    fetch_success = True
                else:
                    error_msg = f"Unknown ATS type '{target.ats_type}' and missing career_url"
            except Exception as e:
                fetch_success = False
                error_msg = str(e)
                logger.warning(
                    f"Target scrape error for '{target.name}' ({target.slug}): {str(e)[:100]}"
                )

        now_iso = datetime.now(timezone.utc).isoformat()
        inserted_count = 0
        live_count = len(jobs) if fetch_success else 0
        archived_count = 0

        if not dry_run:
            if fetch_success:
                if jobs:
                    # Enforce country = India if target is an Indian startup/unicorn
                    if (
                        target.category_tier in ("startup", "unicorn")
                        or "india" in target.slug
                        or "india" in target.name.lower()
                    ):
                        for j in jobs:
                            if j.country in ("Global", "Remote / Global"):
                                j.country = "India"
                    inserted_count = await upsert_jobs(jobs)
                    live_ids = [j.id for j in jobs]
                else:
                    live_ids = []

                reconcile_res = await reconcile_target_jobs(
                    company=target.name,
                    live_job_ids=live_ids,
                    sync_timestamp=now_iso,
                    is_successful_fetch=True,
                )
                live_count = reconcile_res.get("live_count", 0)
                archived_count = reconcile_res.get("archived_count", 0)
            else:
                # Data-loss guard: do not soft-archive existing jobs on error (T-14-02)
                await reconcile_target_jobs(
                    company=target.name,
                    live_job_ids=[],
                    sync_timestamp=now_iso,
                    is_successful_fetch=False,
                )

        return {
            "slug": target.slug,
            "name": target.name,
            "ats_type": target.ats_type,
            "tier": target.category_tier,
            "success": fetch_success,
            "status": "ok" if fetch_success else "error",
            "error": error_msg,
            "jobs_found": len(jobs),
            "jobs_upserted": inserted_count,
            "live_jobs": live_count,
            "archived_jobs": archived_count,
            "dry_run": dry_run,
        }

    async def run(
        self,
        targets: Optional[List[CareerTarget]] = None,
        tier: Optional[str] = None,
        domain: Optional[str] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
        purge_stale_days: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> BatchScrapeResult:
        """
        Executes batch ingestion over a list or query of CareerTarget records.
        """
        start_time = time.time()

        if targets is None:
            params = CareerTargetFilterParams(
                category_tier=tier,
                domain=domain,
                status="active",
                limit=limit or 500,
                offset=0,
            )
            loaded_targets, _ = await get_targets(params)
            targets = loaded_targets

        if limit and len(targets) > limit:
            targets = targets[:limit]

        total_targets = len(targets)
        logger.info(
            f"Starting batch runner: {total_targets} targets, concurrency={self.concurrency}, dry_run={dry_run}"
        )

        completed_details: List[Dict[str, Any]] = []
        successful_count = 0
        failed_count = 0
        total_live_found = 0
        total_upserted = 0
        total_archived = 0

        async def _bounded_target_worker(t: CareerTarget):
            nonlocal successful_count, failed_count, total_live_found, total_upserted, total_archived
            res = await self.scrape_target(t, dry_run=dry_run)
            completed_details.append(res)

            if res["success"]:
                successful_count += 1
                total_live_found += res["jobs_found"]
                total_upserted += res["jobs_upserted"]
                total_archived += res["archived_jobs"]
            else:
                failed_count += 1

            if progress_callback:
                try:
                    progress_callback({
                        "processed": len(completed_details),
                        "total": total_targets,
                        "current_target": t.slug,
                        "success": res["success"],
                        "jobs_found": res["jobs_found"],
                        "live_jobs": total_live_found,
                        "archived_jobs": total_archived,
                    })
                except Exception:
                    pass

        tasks = [_bounded_target_worker(target) for target in targets]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        purged_count = 0
        if purge_stale_days and purge_stale_days > 0:
            purged_count = await purge_stale_jobs(
                days_inactive=purge_stale_days,
                dry_run=dry_run,
            )

        elapsed = max(time.time() - start_time, 0.001)
        throughput = total_live_found / elapsed

        return BatchScrapeResult(
            total_targets=total_targets,
            successful_targets=successful_count,
            failed_targets=failed_count,
            live_jobs_found=total_live_found,
            new_jobs_upserted=total_upserted,
            archived_jobs_count=total_archived,
            purged_jobs_count=purged_count,
            elapsed_seconds=round(elapsed, 2),
            throughput_jobs_per_sec=round(throughput, 1),
            target_details=completed_details,
        )

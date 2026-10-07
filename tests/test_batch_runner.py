import asyncio
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from backend.app.db.database import (
    get_connection,
    init_db,
    purge_stale_jobs,
    reconcile_target_jobs,
    upsert_jobs,
)
from backend.app.models.job import JobItem
from backend.app.models.target import CareerTarget
from backend.app.services.batch_runner import BatchScrapeResult, BatchScrapeRunner
from backend.app.services.sync import JobSyncService


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()


def make_mock_job(job_id: str, company: str, title: str = "Software Engineer", date_offset_days: int = 0) -> JobItem:
    ts = (datetime.now(timezone.utc) - timedelta(days=date_offset_days)).isoformat()
    return JobItem(
        id=job_id,
        title=title,
        company=company,
        domain="Tech",
        category="software_engineering",
        seniority="mid",
        location="Bengaluru, India",
        country="India",
        is_remote=False,
        date_posted=ts,
        apply_url=f"https://careers.example.com/{job_id}",
        source="greenhouse",
    )


@pytest.mark.asyncio
async def test_reconciliation_and_data_loss_guard():
    company = "DataGuard Co"
    job1 = make_mock_job("dg_1", company, "Backend Engineer")
    job2 = make_mock_job("dg_2", company, "Frontend Engineer")

    # Seed 2 live jobs
    await upsert_jobs([job1, job2])
    res_init = await reconcile_target_jobs(
        company=company,
        live_job_ids=["dg_1", "dg_2"],
        is_successful_fetch=True,
    )
    assert res_init["live_count"] == 2
    assert res_init["archived_count"] == 0

    # Verify both are active
    async with get_connection() as db:
        async with db.execute(
            "SELECT COUNT(*) as cnt FROM jobs WHERE company = ? AND is_active = 1",
            [company],
        ) as cur:
            assert (await cur.fetchone())["cnt"] == 2

    # Case 1: Scrape error occurs (is_successful_fetch = False)
    # T-14-02: Must NOT soft-archive or delete existing jobs
    res_err = await reconcile_target_jobs(
        company=company,
        live_job_ids=[],
        is_successful_fetch=False,
    )
    assert res_err["status"] == "error"

    async with get_connection() as db:
        async with db.execute(
            "SELECT COUNT(*) as cnt FROM jobs WHERE company = ? AND is_active = 1",
            [company],
        ) as cur:
            assert (await cur.fetchone())["cnt"] == 2  # Still 2 active jobs!

    # Case 2: Confirmed successful scrape returns only job1 (job2 vanished)
    res_sync = await reconcile_target_jobs(
        company=company,
        live_job_ids=["dg_1"],
        is_successful_fetch=True,
    )
    assert res_sync["status"] == "ok"
    assert res_sync["live_count"] == 1
    assert res_sync["archived_count"] == 1

    async with get_connection() as db:
        async with db.execute(
            "SELECT id, is_active FROM jobs WHERE company = ? ORDER BY id",
            [company],
        ) as cur:
            rows = await cur.fetchall()
            status_map = {r["id"]: r["is_active"] for r in rows}
            assert status_map["dg_1"] == 1
            assert status_map["dg_2"] == 0


@pytest.mark.asyncio
async def test_purge_stale_jobs():
    company = "PurgeTest Inc"
    now = datetime.now(timezone.utc)

    # Job 1: Active job
    j_active = make_mock_job("purge_act", company, "Active Role")
    await upsert_jobs([j_active])

    # Job 2: Inactive job seen 45 days ago
    j_old = make_mock_job("purge_old", company, "Old Role", date_offset_days=45)
    await upsert_jobs([j_old])

    # Job 3: Inactive job seen 10 days ago
    j_recent_inactive = make_mock_job("purge_recent", company, "Recent Inactive", date_offset_days=10)
    await upsert_jobs([j_recent_inactive])

    old_ts = (now - timedelta(days=45)).isoformat()
    recent_ts = (now - timedelta(days=10)).isoformat()

    async with get_connection() as db:
        await db.execute(
            "UPDATE jobs SET is_active = 0, last_seen_at = ? WHERE id = 'purge_old'",
            [old_ts],
        )
        await db.execute(
            "UPDATE jobs SET is_active = 0, last_seen_at = ? WHERE id = 'purge_recent'",
            [recent_ts],
        )
        await db.commit()

    # Dry-run check for threshold 30 days
    dry_count = await purge_stale_jobs(days_inactive=30, dry_run=True)
    assert dry_count >= 1

    # Verify record still exists after dry-run
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as cnt FROM jobs WHERE id = 'purge_old'") as cur:
            assert (await cur.fetchone())["cnt"] == 1

    # Live purge
    purged = await purge_stale_jobs(days_inactive=30, dry_run=False)
    assert purged >= 1

    # Verify purge_old is deleted, purge_recent and purge_act remain
    async with get_connection() as db:
        async with db.execute("SELECT id FROM jobs WHERE id IN ('purge_act', 'purge_old', 'purge_recent')") as cur:
            remaining_ids = [r["id"] for r in await cur.fetchall()]
            assert "purge_old" not in remaining_ids
            assert "purge_act" in remaining_ids
            assert "purge_recent" in remaining_ids


@pytest.mark.asyncio
async def test_error_isolation():
    mock_sync_service = JobSyncService()
    mock_greenhouse = AsyncMock()

    # Company 1 succeeds, Company 2 throws Network Error, Company 3 succeeds
    async def mock_fetch(company_name, company_slug, domain):
        if company_slug == "fail-co":
            raise ConnectionError("Upstream timeout 504")
        return [make_mock_job(f"job_{company_slug}", company_name)]

    mock_greenhouse.fetch_jobs = AsyncMock(side_effect=mock_fetch)
    mock_sync_service.connectors["greenhouse"] = mock_greenhouse

    runner = BatchScrapeRunner(concurrency=5, sync_service=mock_sync_service)

    t1 = CareerTarget.create(name="Alpha Co", career_url="https://alpha.com", ats_type="greenhouse", slug="alpha-co")
    t2 = CareerTarget.create(name="Fail Co", career_url="https://fail.com", ats_type="greenhouse", slug="fail-co")
    t3 = CareerTarget.create(name="Gamma Co", career_url="https://gamma.com", ats_type="greenhouse", slug="gamma-co")

    res = await runner.run(targets=[t1, t2, t3], dry_run=True)

    assert res.total_targets == 3
    assert res.successful_targets == 2
    assert res.failed_targets == 1
    assert res.live_jobs_found == 2

    # Check detail outputs
    status_map = {d["slug"]: d["success"] for d in res.target_details}
    assert status_map["alpha-co"] is True
    assert status_map["fail-co"] is False
    assert status_map["gamma-co"] is True


@pytest.mark.asyncio
async def test_batch_runner_concurrency():
    mock_sync_service = JobSyncService()
    mock_connector = AsyncMock()

    active_concurrent = 0
    max_observed_concurrent = 0
    lock = asyncio.Lock()

    async def mock_fetch_with_timing(company_name, company_slug, domain):
        nonlocal active_concurrent, max_observed_concurrent
        async with lock:
            active_concurrent += 1
            if active_concurrent > max_observed_concurrent:
                max_observed_concurrent = active_concurrent

        await asyncio.sleep(0.05)

        async with lock:
            active_concurrent -= 1
        return [make_mock_job(f"job_{company_slug}", company_name)]

    mock_connector.fetch_jobs = AsyncMock(side_effect=mock_fetch_with_timing)
    mock_sync_service.connectors["greenhouse"] = mock_connector

    concurrency_limit = 3
    runner = BatchScrapeRunner(
        concurrency=concurrency_limit,
        default_jitter_range=(0.0, 0.01),
        sync_service=mock_sync_service,
    )

    targets = [
        CareerTarget.create(name=f"Comp {i}", career_url="https://x.com", ats_type="greenhouse", slug=f"comp-{i}")
        for i in range(8)
    ]

    res = await runner.run(targets=targets, dry_run=True)

    assert res.total_targets == 8
    assert res.successful_targets == 8
    # Max concurrency observed must not exceed semaphore limit
    assert max_observed_concurrent <= concurrency_limit


def test_sync_batch_cli_args():
    # Test --help output
    res_help = subprocess.run(
        [sys.executable, "backend/scripts/sync_batch.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert res_help.returncode == 0
    assert "--concurrency" in res_help.stdout
    assert "--purge-stale" in res_help.stdout
    assert "--dry-run" in res_help.stdout

    # Test main execution flow with mocked runner to avoid external ATS network calls
    with patch("backend.scripts.sync_batch.BatchScrapeRunner.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = BatchScrapeResult(
            total_targets=1,
            successful_targets=1,
            failed_targets=0,
            live_jobs_found=5,
            new_jobs_upserted=5,
            archived_jobs_count=0,
            purged_jobs_count=0,
            elapsed_seconds=0.1,
            throughput_jobs_per_sec=50.0,
            target_details=[{"slug": "test-target", "success": True}],
        )

        with patch("sys.argv", ["sync_batch.py", "--limit", "1", "--dry-run", "--quiet"]):
            from backend.scripts.sync_batch import main
            asyncio.run(main())
            mock_run.assert_called_once()

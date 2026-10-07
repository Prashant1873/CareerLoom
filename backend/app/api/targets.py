import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.app.db.database import (
    get_targets,
    get_target_by_slug,
    get_target_stats,
    purge_stale_jobs,
)
from backend.app.models.target import (
    CareerTarget,
    CareerTargetFilterParams,
    CareerTargetStats,
)
from backend.app.services.scheduler import batch_scheduler
from backend.app.services.sync import JobSyncService
from fastapi.responses import JSONResponse

logger = logging.getLogger("careerloom.api.targets")

router = APIRouter(prefix="/api/targets", tags=["Career Targets Registry"])
_sync_service = JobSyncService()


@router.get("", response_model=Dict[str, Any])
async def list_targets(
    tier: Optional[str] = Query(None, description="Filter by category tier: startup, unicorn, enterprise, consulting"),
    domain: Optional[str] = Query(None, description="Filter by industry domain"),
    role_tag: Optional[str] = Query(None, description="Filter by role tag: product, strategy, tech, founders_office"),
    status: Optional[str] = Query(None, description="Filter by status: active, syncing, error, paused"),
    search: Optional[str] = Query(None, description="Search query by company name, slug, or domain"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Retrieves paginated career targets from the registry with faceted filters.
    """
    params = CareerTargetFilterParams(
        category_tier=tier,
        domain=domain,
        role_tag=role_tag,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
    )
    items, total = await get_targets(params)
    return {
        "items": [item.model_dump() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats", response_model=CareerTargetStats)
async def target_stats():
    """
    Returns aggregate target statistics: total monitored companies, active counts, tier distribution, and live jobs.
    """
    return await get_target_stats()


@router.post("/sync")
async def trigger_batch_sync(
    tier: Optional[str] = Query(None, description="Filter targets by tier"),
    domain: Optional[str] = Query(None, description="Filter targets by domain"),
    limit: Optional[int] = Query(None, description="Limit targets to sync"),
    concurrency: int = Query(15, ge=1, le=50, description="Concurrency limit"),
):
    """
    Triggers an on-demand batch synchronization across career targets in the background (BATCH-03).
    Returns HTTP 202 Accepted if started, or HTTP 409 Conflict if a sync is already running (T-14-01).
    """
    started = await batch_scheduler.trigger_now(
        tier=tier,
        domain=domain,
        limit=limit,
        concurrency=concurrency,
    )
    if not started:
        raise HTTPException(
            status_code=409,
            detail="Batch synchronization is already in progress",
        )

    return JSONResponse(
        status_code=202,
        content={
            "status": "started",
            "message": "Batch synchronization initiated in background",
            "filters": {"tier": tier, "domain": domain, "limit": limit, "concurrency": concurrency},
        },
    )


@router.get("/sync/status")
async def get_sync_status():
    """
    Retrieves the real-time execution status, target progress, and metrics of the batch scheduler.
    """
    return batch_scheduler.get_status()


@router.post("/purge-stale")
async def purge_stale_postings(
    days_inactive: int = Query(30, ge=1, description="Days threshold to consider postings dead"),
    dry_run: bool = Query(False, description="Simulate purge without deleting records"),
):
    """
    Permanently purges postings that have remained inactive for >days_inactive days (BATCH-02).
    """
    purged = await purge_stale_jobs(days_inactive=days_inactive, dry_run=dry_run)
    return {
        "purged_count": purged,
        "days_inactive": days_inactive,
        "dry_run": dry_run,
    }


@router.get("/{slug}", response_model=CareerTarget)
async def get_target(slug: str):
    """
    Retrieves a single career target by slug.
    """
    target = await get_target_by_slug(slug)
    if not target:
        raise HTTPException(status_code=404, detail=f"Target '{slug}' not found")
    return target


@router.post("/{slug}/sync")
async def sync_single_target(slug: str):
    """
    Triggers an on-demand synchronization pass for a single career target.
    """
    target = await get_target_by_slug(slug)
    if not target:
        raise HTTPException(status_code=404, detail=f"Target '{slug}' not found")

    result = await _sync_service.sync_target(target)
    return result

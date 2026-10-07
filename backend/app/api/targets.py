import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.app.db.database import (
    get_targets,
    get_target_by_slug,
    get_target_stats,
)
from backend.app.models.target import (
    CareerTarget,
    CareerTargetFilterParams,
    CareerTargetStats,
)
from backend.app.services.sync import JobSyncService

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

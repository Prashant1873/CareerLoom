import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.taxonomy import (
    CATEGORY_CLUSTERS,
    get_all_categories,
    get_category_by_id,
    match_category_phrase,
)

logger = logging.getLogger("careerloom.api.categories")
router = APIRouter(prefix="/api/categories", tags=["Categories"])

_TRACK_COUNTS_CACHE: Dict[str, int] = {}
_TRACK_COUNTS_EXPIRY: float = 0.0


async def _get_cached_track_counts() -> Dict[str, int]:
    """Retrieves active job counts per track with a 60-second in-memory TTL cache."""
    global _TRACK_COUNTS_CACHE, _TRACK_COUNTS_EXPIRY
    now = time.time()
    if _TRACK_COUNTS_CACHE and now < _TRACK_COUNTS_EXPIRY:
        return _TRACK_COUNTS_CACHE

    counts: Dict[str, int] = {}
    try:
        from backend.app.db.database import get_connection
        async with get_connection() as db:
            async with db.execute(
                "SELECT track, COUNT(*) as cnt FROM jobs WHERE is_active = 1 AND track IS NOT NULL GROUP BY track"
            ) as cursor:
                rows = await cursor.fetchall()
                for r in rows:
                    if r["track"]:
                        counts[r["track"].lower()] = r["cnt"]
    except Exception as e:
        logger.warning(f"Error fetching track counts: {e}")

    _TRACK_COUNTS_CACHE = counts
    _TRACK_COUNTS_EXPIRY = now + 60.0
    return counts


class CategoryResponse(BaseModel):
    id: str
    cluster: Optional[str] = None
    label: str
    description: str
    icon: str
    curated_tracks: List[str]
    related_skills: List[str]


class CategoriesListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]


@router.get("", response_model=CategoriesListResponse)
async def list_categories():
    """
    Returns full catalog of canonical job role categories and discovery tracks.
    Used for category navigation and search pill suggestions.
    """
    cats = get_all_categories()
    return CategoriesListResponse(
        total=len(cats),
        categories=[
            CategoryResponse(
                id=c["id"],
                cluster=c.get("cluster"),
                label=c["label"],
                description=c["description"],
                icon=c["icon"],
                curated_tracks=c["curated_tracks"],
                related_skills=c["related_skills"],
            )
            for c in cats
        ],
    )


@router.get("/clusters")
async def list_category_clusters():
    """
    Returns all domain clusters, their display labels, descriptions, and member categories.
    """
    clusters = list(CATEGORY_CLUSTERS.values())
    return {"total": len(clusters), "clusters": clusters}


@router.get("/tracks")
async def list_discovery_tracks():
    """
    Returns flat list of curated discovery tracks for quick-pill exploration
    enriched with parent cluster IDs and cached active job counts.
    """
    cats = get_all_categories()
    track_counts = await _get_cached_track_counts()
    tracks = []
    for c in cats:
        for t in c["curated_tracks"]:
            count = track_counts.get(t.lower(), 0)
            tracks.append({
                "track": t,
                "category_id": c["id"],
                "category_label": c["label"],
                "cluster_id": c.get("cluster"),
                "job_count": count,
            })
    return {"total": len(tracks), "tracks": tracks}


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """
    Returns detailed metadata for a single canonical category.
    """
    cat = get_category_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")
    return CategoryResponse(
        id=cat["id"],
        cluster=cat.get("cluster"),
        label=cat["label"],
        description=cat["description"],
        icon=cat["icon"],
        curated_tracks=cat["curated_tracks"],
        related_skills=cat["related_skills"],
    )

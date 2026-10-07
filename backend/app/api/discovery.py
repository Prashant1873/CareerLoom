import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.db.database import get_cached_discovery_posts
from backend.app.services.discovery_prober import get_discovery_prober
from backend.app.services.reddit_scanner import get_reddit_scanner

logger = logging.getLogger("careerloom.discovery_api")
router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoveryPostItem(BaseModel):
    id: str
    subreddit: str
    title: str
    selftext: Optional[str] = ""
    url: Optional[str] = ""
    permalink: Optional[str] = ""
    score: Optional[int] = 0
    num_comments: Optional[int] = 0
    author: Optional[str] = ""
    created_utc: Optional[float] = 0


class DiscoveryScanResponse(BaseModel):
    status: str
    total_posts: int
    candidates_found: int
    targets_enrolled: int
    enrolled_slugs: List[str]
    breakdown_by_subreddit: Dict[str, int]


@router.get("/feed", response_model=List[DiscoveryPostItem])
async def get_discovery_feed(
    subreddit: Optional[str] = Query(None, description="Filter by subreddit e.g. 'developersIndia'"),
    limit: int = Query(50, ge=1, le=200, description="Max posts to return"),
) -> List[DiscoveryPostItem]:
    """
    Returns unexpired Reddit career and tech discussion posts cached in SQLite.
    """
    posts = await get_cached_discovery_posts(subreddit=subreddit, limit=limit)
    return [
        DiscoveryPostItem(
            id=str(p.get("id", "")),
            subreddit=str(p.get("subreddit", "")),
            title=str(p.get("title", "")),
            selftext=str(p.get("selftext", "")),
            url=str(p.get("url", "")),
            permalink=str(p.get("permalink", "")),
            score=int(p.get("score", 0)),
            num_comments=int(p.get("num_comments", 0)),
            author=str(p.get("author", "")),
            created_utc=float(p.get("created_utc", 0)),
        )
        for p in posts
    ]


@router.post("/scan", response_model=DiscoveryScanResponse)
async def trigger_discovery_scan(
    force_refresh: bool = Query(False, description="Bypass 24h cache and fetch fresh Reddit feeds"),
) -> DiscoveryScanResponse:
    """
    Triggers Reddit discovery scan across target subreddits, extracts company mentions,
    probes canonical ATS endpoints, and enrolls verified targets into career_targets.
    """
    try:
        scanner = get_reddit_scanner()
        prober = get_discovery_prober()

        scan_result = await scanner.scan_all_subreddits(force_refresh=force_refresh)
        posts = scan_result.get("posts", [])

        probe_result = await prober.process_discovery_posts(posts)

        return DiscoveryScanResponse(
            status="ok",
            total_posts=scan_result.get("total_posts", 0),
            candidates_found=probe_result.get("candidates_found", 0),
            targets_enrolled=probe_result.get("targets_enrolled", 0),
            enrolled_slugs=probe_result.get("enrolled_slugs", []),
            breakdown_by_subreddit=scan_result.get("breakdown", {}),
        )
    except Exception as e:
        logger.error(f"Discovery scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

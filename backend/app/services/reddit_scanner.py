import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx

from backend.app.db.database import get_cached_discovery_posts, save_discovery_posts

logger = logging.getLogger("careerloom.reddit_scanner")

TARGET_SUBREDDITS = [
    "developersIndia",
    "IndianStartups",
    "ProductManagement",
    "consulting",
    "bangalore",
]

DEFAULT_USER_AGENT = "CareerLoom-Discovery/1.0 (Contact: discovery@careerloom.local)"


class RedditDiscoveryService:
    """
    Automated scanner for public Reddit career and tech communities with 24h TTL caching,
    polite delay rate limiting, and graceful degradation on HTTP 429 rate limits.
    """

    def __init__(
        self,
        subreddits: Optional[List[str]] = None,
        user_agent: str = DEFAULT_USER_AGENT,
        request_delay_seconds: float = 1.0,
    ):
        self.subreddits = subreddits or TARGET_SUBREDDITS
        self.user_agent = user_agent
        self.request_delay_seconds = request_delay_seconds

    async def fetch_subreddit_posts(
        self,
        subreddit: str,
        force_refresh: bool = False,
        limit_per_feed: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Fetches hot and hiring-specific posts for a subreddit, with 24h cache check.
        """
        clean_sub = subreddit.replace("r/", "").strip()
        if not clean_sub:
            return []

        # 1. Check SQLite 24h cache if not force refreshing
        if not force_refresh:
            cached = await get_cached_discovery_posts(clean_sub, limit=50)
            if cached:
                logger.info(f"Serving {len(cached)} cached discovery posts for r/{clean_sub}")
                return cached

        posts_map: Dict[str, Dict[str, Any]] = {}
        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            # 1. Hot feed query
            hot_url = f"https://www.reddit.com/r/{clean_sub}/hot.json?limit={limit_per_feed}"
            try:
                resp = await client.get(hot_url)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for c in children:
                        d = c.get("data", {})
                        pid = d.get("id")
                        if pid:
                            posts_map[pid] = {
                                "id": pid,
                                "subreddit": clean_sub,
                                "title": d.get("title", ""),
                                "selftext": d.get("selftext", ""),
                                "url": d.get("url", f"https://www.reddit.com{d.get('permalink', '')}"),
                                "permalink": d.get("permalink", ""),
                                "score": d.get("score", 0),
                                "num_comments": d.get("num_comments", 0),
                                "author": d.get("author", ""),
                                "created_utc": d.get("created_utc", 0),
                            }
                elif resp.status_code == 429:
                    logger.warning(f"Reddit 429 rate limit hit for r/{clean_sub} hot feed. Backing off.")
            except Exception as e:
                logger.warning(f"Failed fetching hot feed for r/{clean_sub}: {e}")

            # Polite inter-request delay
            await asyncio.sleep(self.request_delay_seconds)

            # 2. Targeted hiring search query
            search_query = quote_plus("hiring OR openings OR careers OR referral OR who is hiring")
            search_url = (
                f"https://www.reddit.com/r/{clean_sub}/search.json"
                f"?q={search_query}&restrict_sr=1&sort=new&limit={limit_per_feed}"
            )
            try:
                resp = await client.get(search_url)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for c in children:
                        d = c.get("data", {})
                        pid = d.get("id")
                        if pid and pid not in posts_map:
                            posts_map[pid] = {
                                "id": pid,
                                "subreddit": clean_sub,
                                "title": d.get("title", ""),
                                "selftext": d.get("selftext", ""),
                                "url": d.get("url", f"https://www.reddit.com{d.get('permalink', '')}"),
                                "permalink": d.get("permalink", ""),
                                "score": d.get("score", 0),
                                "num_comments": d.get("num_comments", 0),
                                "author": d.get("author", ""),
                                "created_utc": d.get("created_utc", 0),
                            }
                elif resp.status_code == 429:
                    logger.warning(f"Reddit 429 rate limit hit for r/{clean_sub} search feed. Backing off.")
            except Exception as e:
                logger.warning(f"Failed fetching search feed for r/{clean_sub}: {e}")

        posts_list = list(posts_map.values())
        if posts_list:
            await save_discovery_posts(posts_list, ttl_hours=24)
            logger.info(f"Cached {len(posts_list)} posts for r/{clean_sub}")
        else:
            # If fetch returned nothing (e.g. offline/blocked), fallback to any stale cache
            cached = await get_cached_discovery_posts(clean_sub, limit=50)
            if cached:
                logger.info(f"Fallback to existing cache for r/{clean_sub} ({len(cached)} posts)")
                return cached

        return posts_list

    async def scan_all_subreddits(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes bounded concurrent scanning across all target subreddits.
        """
        semaphore = asyncio.Semaphore(2)  # Conservative concurrency for polite polling
        all_posts: List[Dict[str, Any]] = []
        status_by_sub: Dict[str, int] = {}

        async def _scan_sub(sub: str):
            async with semaphore:
                posts = await self.fetch_subreddit_posts(sub, force_refresh=force_refresh)
                status_by_sub[sub] = len(posts)
                all_posts.extend(posts)
                await asyncio.sleep(self.request_delay_seconds)

        tasks = [_scan_sub(s) for s in self.subreddits]
        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "total_posts": len(all_posts),
            "subreddits_scanned": len(self.subreddits),
            "breakdown": status_by_sub,
            "posts": all_posts,
        }


_scanner_instance: Optional[RedditDiscoveryService] = None


def get_reddit_scanner() -> RedditDiscoveryService:
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = RedditDiscoveryService()
    return _scanner_instance

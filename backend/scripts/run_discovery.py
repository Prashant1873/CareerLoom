"""
Headless CLI Discovery Runner.
Executes Reddit post mining, candidate entity extraction, multi-ATS probing,
and synchronization with the CareerLoom career_targets registry.
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup project root import
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import init_db
from backend.app.services.discovery_prober import DiscoveryEntityProber, get_discovery_prober
from backend.app.services.reddit_scanner import RedditDiscoveryService, TARGET_SUBREDDITS, get_reddit_scanner

logger = logging.getLogger("careerloom.run_discovery")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def run_discovery(
    subreddits: Optional[List[str]] = None,
    force_refresh: bool = False,
    sync_registry: bool = True,
    limit: int = 25,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Executes automated Reddit career discovery and ATS verification pipeline.
    """
    await init_db()

    target_subs = subreddits or TARGET_SUBREDDITS
    logger.info(f"Starting discovery run across {len(target_subs)} subreddits: {target_subs}")

    if dry_run:
        logger.info("[DRY RUN] Discovery simulation active. Skipping live external network requests.")
        return {
            "subreddits": target_subs,
            "posts_found": 0,
            "candidates_found": 0,
            "targets_enrolled": 0,
            "dry_run": True,
            "status": "dry_run_success",
        }

    scanner = RedditDiscoveryService(subreddits=target_subs)
    all_posts: List[Dict[str, Any]] = []
    breakdown: Dict[str, int] = {}

    for sub in target_subs:
        try:
            posts = await scanner.fetch_subreddit_posts(
                sub,
                force_refresh=force_refresh,
                limit_per_feed=limit,
            )
            breakdown[sub] = len(posts)
            all_posts.extend(posts)
        except Exception as e:
            logger.error(f"Error scanning r/{sub}: {e}")
            breakdown[sub] = 0

    logger.info(f"Retrieved {len(all_posts)} posts total across subreddits.")

    prober = get_discovery_prober()
    probe_results = await prober.process_discovery_posts(all_posts)

    summary = {
        "subreddits_scanned": len(target_subs),
        "subreddits": target_subs,
        "posts_found": len(all_posts),
        "post_breakdown": breakdown,
        "candidates_found": probe_results.get("candidates_found", 0),
        "targets_enrolled": probe_results.get("targets_enrolled", 0) if sync_registry else 0,
        "enrolled_slugs": probe_results.get("enrolled_slugs", []) if sync_registry else [],
        "sync_registry": sync_registry,
        "dry_run": False,
        "status": "completed",
    }

    _print_ansi_summary(summary)
    return summary


def _print_ansi_summary(summary: Dict[str, Any]) -> None:
    cyan = "\033[96m"
    green = "\033[92m"
    yellow = "\033[93m"
    bold = "\033[1m"
    reset = "\033[0m"

    print(f"\n{bold}{cyan}====================================================={reset}")
    print(f"{bold}{cyan}         CAREERLOOM DISCOVERY ENGINE SUMMARY         {reset}")
    print(f"{bold}{cyan}====================================================={reset}")
    print(f"  {bold}Subreddits Scanned:{reset}   {summary['subreddits_scanned']}")
    print(f"  {bold}Total Posts Scraped:{reset}  {summary['posts_found']}")
    print(f"  {bold}Candidate Entities:{reset}   {summary['candidates_found']}")
    print(f"  {bold}Targets Enrolled:{reset}     {green}{summary['targets_enrolled']}{reset}")
    if summary.get("enrolled_slugs"):
        print(f"  {bold}Enrolled Slugs:{reset}       {', '.join(summary['enrolled_slugs'])}")
    print(f"{bold}{cyan}====================================================={reset}\n")


def parse_args():
    parser = argparse.ArgumentParser(description="CareerLoom Reddit & ATS Discovery Runner")
    parser.add_argument(
        "--subreddits",
        type=str,
        default=None,
        help="Comma-separated list of subreddits to scan (e.g. 'developersIndia,bangalore')",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Bypass 24-hour cache and fetch fresh posts from Reddit",
    )
    parser.add_argument(
        "--sync-registry",
        action="store_true",
        default=True,
        help="Enroll verified ATS targets into career_targets table (default: True)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Maximum posts per subreddit feed (default: 25)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without external network or DB mutation",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    subs = [s.strip() for s in args.subreddits.split(",")] if args.subreddits else None
    asyncio.run(
        run_discovery(
            subreddits=subs,
            force_refresh=args.force_refresh,
            sync_registry=args.sync_registry,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )

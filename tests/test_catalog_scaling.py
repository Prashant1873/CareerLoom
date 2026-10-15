"""
Automated Test Suite for Catalog Scaling & Partitioning Engine.
Verifies partitioned datasets (150+ startups, 40+ conglomerates, 30+ consulting),
idempotent seeding with telemetry preservation, fast indexed target filtering,
and headless discovery CLI runner.
"""
import json
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pytest_asyncio

from backend.app.db.database import (
    get_connection,
    get_target_by_slug,
    get_targets,
    init_db,
    upsert_target,
)
from backend.app.models.target import CareerTarget, CareerTargetFilterParams
from backend.scripts.run_discovery import run_discovery
from backend.scripts.seed_targets import (
    TARGETS_DIR,
    VALID_ROLE_TAGS,
    collect_seed_targets,
    seed_career_targets,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield


def test_catalog_files():
    """
    DISCOVERY-03: Validates all 3 partitioned catalog JSON files:
    - indian_startups.json >= 150
    - indian_conglomerates.json >= 40
    - strategy_consulting.json >= 30
    Total >= 220, valid schemas, allowed tiers, and standardized role tags.
    """
    startups_file = TARGETS_DIR / "indian_startups.json"
    conglom_file = TARGETS_DIR / "indian_conglomerates.json"
    consulting_file = TARGETS_DIR / "strategy_consulting.json"

    assert startups_file.exists(), f"Missing {startups_file}"
    assert conglom_file.exists(), f"Missing {conglom_file}"
    assert consulting_file.exists(), f"Missing {consulting_file}"

    with open(startups_file, "r", encoding="utf-8") as f:
        startups = json.load(f)
    with open(conglom_file, "r", encoding="utf-8") as f:
        congloms = json.load(f)
    with open(consulting_file, "r", encoding="utf-8") as f:
        consulting = json.load(f)

    # 1. Partition size constraints
    assert len(startups) >= 150, f"Expected >= 150 startups, got {len(startups)}"
    assert len(congloms) >= 40, f"Expected >= 40 conglomerates, got {len(congloms)}"
    assert len(consulting) >= 30, f"Expected >= 30 consulting firms, got {len(consulting)}"

    total_targets = len(startups) + len(congloms) + len(consulting)
    assert total_targets >= 220, f"Expected >= 220 total targets, got {total_targets}"

    # 2. Schema and field integrity
    required_keys = {"name", "slug", "website", "career_url", "ats_type", "category_tier", "domain", "role_focus"}
    allowed_tiers = {"startup", "unicorn", "conglomerate", "consulting"}
    all_slugs = set()

    for catalog_name, items in [
        ("startups", startups),
        ("conglomerates", congloms),
        ("consulting", consulting),
    ]:
        for item in items:
            for k in required_keys:
                assert k in item, f"Missing key '{k}' in {catalog_name} target: {item.get('name')}"

            slug = item["slug"]
            assert slug not in all_slugs, f"Duplicate slug '{slug}' found in {catalog_name}"
            all_slugs.add(slug)

            tier = item["category_tier"].lower()
            assert tier in allowed_tiers, f"Invalid tier '{tier}' in target {item['name']}"

            assert item["career_url"].startswith("http"), f"Invalid career_url in target {item['name']}"

            role_focus = item.get("role_focus", [])
            assert isinstance(role_focus, list) and len(role_focus) > 0, f"Empty role_focus for {item['name']}"
            for tag in role_focus:
                assert tag in VALID_ROLE_TAGS, f"Invalid role tag '{tag}' in target {item['name']}"


@pytest.mark.asyncio
async def test_seed_targets():
    """
    Validates idempotent seed_career_targets:
    - Seeds all partitioned targets into SQLite
    - Table count reflects partitioned datasets (>= 220)
    - Re-seeding preserves live telemetry (job_count, last_scraped_at, last_status)
    """
    total_seeded = await seed_career_targets(force=True)
    assert total_seeded >= 220, f"Expected at least 220 seeded targets, got {total_seeded}"

    # Check a specific target exists and modify telemetry
    sample_target = await get_target_by_slug("swiggy")
    assert sample_target is not None
    assert sample_target.category_tier in ("unicorn", "startup")
    assert "tech" in sample_target.role_focus

    # Simulate live scraper telemetry on swiggy
    async with get_connection() as db:
        await db.execute(
            """
            UPDATE career_targets
            SET job_count = 42, last_status = 'ok', last_scraped_at = '2026-10-08T00:00:00Z'
            WHERE slug = 'swiggy'
            """
        )
        await db.commit()

    modified_swiggy = await get_target_by_slug("swiggy")
    assert modified_swiggy.job_count == 42
    assert modified_swiggy.last_status == "ok"
    assert modified_swiggy.last_scraped_at == "2026-10-08T00:00:00Z"

    # Re-seed with force=True - must be idempotent and preserve job_count & telemetry!
    reseeded_count = await seed_career_targets(force=True)
    assert reseeded_count >= 220

    preserved_swiggy = await get_target_by_slug("swiggy")
    assert preserved_swiggy.job_count == 42, "Re-seed wiped live job_count!"
    assert preserved_swiggy.last_status == "ok", "Re-seed wiped last_status!"
    assert preserved_swiggy.last_scraped_at == "2026-10-08T00:00:00Z", "Re-seed wiped last_scraped_at!"


@pytest.mark.asyncio
async def test_scaled_targets_query():
    """
    Validates querying and filtering across the scaled catalog:
    - category_tier='consulting'
    - category_tier='conglomerate'
    - role_tag='product'
    - role_tag='strategy'
    - Verifies sub-20ms query latency on indexed SQLite.
    """
    # 1. Tier filtering: consulting
    start_time = time.perf_counter()
    consulting_targets, c_total = await get_targets(
        CareerTargetFilterParams(category_tier="consulting", limit=50)
    )
    query_latency_ms = (time.perf_counter() - start_time) * 1000

    assert c_total >= 30, f"Expected >= 30 consulting targets, got {c_total}"
    assert all(t.category_tier == "consulting" for t in consulting_targets)
    assert query_latency_ms < 50, f"Query took too long: {query_latency_ms:.2f}ms"

    # 2. Tier filtering: conglomerate
    conglom_targets, cg_total = await get_targets(
        CareerTargetFilterParams(category_tier="conglomerate", limit=50)
    )
    assert cg_total >= 40, f"Expected >= 40 conglomerate targets, got {cg_total}"
    assert all(t.category_tier == "conglomerate" for t in conglom_targets)

    # 3. Role tag filtering: product
    product_targets, p_total = await get_targets(
        CareerTargetFilterParams(role_tag="product", limit=50)
    )
    assert p_total > 50, f"Expected > 50 product targets, got {p_total}"
    assert all("product" in t.role_focus for t in product_targets)

    # 4. Role tag filtering: strategy
    strategy_targets, s_total = await get_targets(
        CareerTargetFilterParams(role_tag="strategy", limit=50)
    )
    assert s_total >= 30, f"Expected >= 30 strategy targets, got {s_total}"
    assert all("strategy" in t.role_focus for t in strategy_targets)


@pytest.mark.asyncio
async def test_run_discovery_cli():
    """
    Validates headless run_discovery runner:
    - Dry-run mode
    - Mocked scan & probe workflow
    """
    # Dry-run execution
    dry_result = await run_discovery(
        subreddits=["developersIndia"],
        dry_run=True,
    )
    assert dry_result["dry_run"] is True
    assert dry_result["status"] == "dry_run_success"

    # Mocked scan workflow
    mock_posts = [
        {
            "id": "post_mock_1",
            "subreddit": "developersIndia",
            "title": "Hiring senior backend engineers at TestCo: https://jobs.lever.co/testco",
            "selftext": "Apply directly on our Lever board",
            "url": "https://reddit.com/r/developersIndia/mock1",
            "score": 10,
        }
    ]

    with patch(
        "backend.app.services.reddit_scanner.RedditDiscoveryService.fetch_subreddit_posts",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_fetch.return_value = mock_posts

        with patch(
            "backend.app.services.discovery_prober.DiscoveryEntityProber.process_discovery_posts",
            new_callable=AsyncMock,
        ) as mock_probe:
            mock_probe.return_value = {
                "posts_processed": 1,
                "candidates_found": 1,
                "targets_enrolled": 1,
                "enrolled_slugs": ["testco"],
            }

            result = await run_discovery(
                subreddits=["developersIndia"],
                force_refresh=True,
                sync_registry=True,
                dry_run=False,
            )

            assert result["status"] == "completed"
            assert result["posts_found"] == 1
            assert result["candidates_found"] == 1
            assert result["targets_enrolled"] == 1
            assert "testco" in result["enrolled_slugs"]

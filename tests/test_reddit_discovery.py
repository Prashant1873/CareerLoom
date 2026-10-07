import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx
from fastapi.testclient import TestClient

from backend.app.db.database import (
    get_cached_discovery_posts,
    get_connection,
    get_target_by_slug,
    init_db,
    is_domain_probed,
    record_probed_domain,
    save_discovery_posts,
)
from backend.app.main import app
from backend.app.services.discovery_prober import DiscoveryEntityProber, get_discovery_prober
from backend.app.services.reddit_scanner import RedditDiscoveryService, get_reddit_scanner


@pytest_asyncio.fixture(autouse=True)
async def ensure_db():
    await init_db()
    async with get_connection() as db:
        await db.execute("DELETE FROM probed_cache WHERE domain_or_slug LIKE 'test-%' OR domain_or_slug = 'example-non-ats'")
        await db.execute("DELETE FROM career_targets WHERE slug LIKE 'test-%'")
        await db.execute("DELETE FROM discovery_cache WHERE post_id LIKE 'post_10%' OR post_id LIKE 'thread_%'")
        await db.commit()
    yield


@pytest.mark.asyncio
async def test_discovery_cache():
    sample_posts = [
        {
            "id": "post_101",
            "subreddit": "developersIndia",
            "title": "Hiring at Cred for Backend Engineer",
            "selftext": "Check out our roles at cred",
            "url": "https://reddit.com/r/developersIndia/101",
            "score": 42,
        },
        {
            "id": "post_102",
            "subreddit": "developersIndia",
            "title": "Razorpay opening for Product Manager",
            "selftext": "Reach out for referral",
            "url": "https://reddit.com/r/developersIndia/102",
            "score": 25,
        },
    ]

    saved = await save_discovery_posts(sample_posts, ttl_hours=24)
    assert saved == 2

    # Query cached posts
    cached = await get_cached_discovery_posts("developersIndia", limit=10)
    assert len(cached) >= 2
    titles = [p["title"] for p in cached]
    assert "Hiring at Cred for Backend Engineer" in titles

    # Test probed cache
    await record_probed_domain("example-non-ats", "non_ats", ttl_days=7)
    status = await is_domain_probed("example-non-ats")
    assert status == "non_ats"

    # Non-existent probed domain
    assert await is_domain_probed("unknown-domain-xyz") is None


@pytest.mark.asyncio
async def test_reddit_scanner():
    scanner = RedditDiscoveryService(subreddits=["developersIndia"], request_delay_seconds=0.01)

    mock_hot_json = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "thread_abc",
                        "title": "Zepto is hiring fast-track APMs",
                        "selftext": "Apply at https://jobs.lever.co/zepto",
                        "permalink": "/r/developersIndia/comments/thread_abc",
                        "score": 50,
                    }
                }
            ]
        }
    }

    mock_search_json = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "thread_xyz",
                        "title": "Referral for Swiggy SDE-2",
                        "selftext": "Send resumes to my DM",
                        "permalink": "/r/developersIndia/comments/thread_xyz",
                        "score": 15,
                    }
                }
            ]
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Mock hot response then search response
        mock_resp_hot = MagicMock(status_code=200, json=lambda: mock_hot_json)
        mock_resp_search = MagicMock(status_code=200, json=lambda: mock_search_json)
        mock_get.side_effect = [mock_resp_hot, mock_resp_search]

        posts = await scanner.fetch_subreddit_posts("developersIndia", force_refresh=True)
        assert len(posts) == 2
        pids = [p["id"] for p in posts]
        assert "thread_abc" in pids
        assert "thread_xyz" in pids

    # Second call without force_refresh should hit SQLite cache directly
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get_second:
        cached_posts = await scanner.fetch_subreddit_posts("developersIndia", force_refresh=False)
        assert len(cached_posts) >= 2
        mock_get_second.assert_not_called()


@pytest.mark.asyncio
async def test_reddit_scanner_graceful_429():
    scanner = RedditDiscoveryService(subreddits=["developersIndia"], request_delay_seconds=0.01)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(status_code=429)
        # Should not throw exception, degrades gracefully
        posts = await scanner.fetch_subreddit_posts("developersIndia", force_refresh=True)
        assert isinstance(posts, list)


@pytest.mark.asyncio
async def test_ats_prober():
    prober = DiscoveryEntityProber(probe_timeout_seconds=1.0)

    # 1. Test candidate extraction
    sample_text = (
        "Hey everyone, Groww is hiring across tech! Also check out https://jobs.ashbyhq.com/signoz "
        "and https://boards.greenhouse.io/atlan/jobs/123."
    )
    candidates = prober.extract_candidates_from_text(sample_text)
    candidate_slugs = [c[0].lower() for c in candidates]
    assert "signoz" in candidate_slugs or "atlan" in candidate_slugs

    # 2. Test probing valid Ashby candidate
    mock_ashby_response = {
        "jobs": [
            {"id": "job-1", "title": "Software Engineer", "location": "Bangalore"}
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_resp = MagicMock(status_code=200, json=lambda: mock_ashby_response)
        mock_get.return_value = mock_resp

        target = await prober.probe_ats_candidate("test-startup-ai", hint_ats="ashby")
        assert target is not None
        assert target.slug == "test-startup-ai"
        assert target.ats_type == "ashby"
        assert target.job_count == 1

        # Verify target is persisted in database
        db_target = await get_target_by_slug("test-startup-ai")
        assert db_target is not None
        assert db_target.name == "Test-Startup-Ai"

        # Verify negative cache prevents re-probing
        status = await is_domain_probed("test-startup-ai")
        assert status == "verified"


@pytest.mark.asyncio
async def test_discovery_api():
    client = TestClient(app)

    # 1. Test GET /api/discovery/feed
    res = client.get("/api/discovery/feed?limit=5")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 2. Test POST /api/discovery/scan with mocked scanner and prober
    with patch("backend.app.services.reddit_scanner.RedditDiscoveryService.scan_all_subreddits") as mock_scan, \
         patch("backend.app.services.discovery_prober.DiscoveryEntityProber.process_discovery_posts") as mock_probe:

        mock_scan.return_value = {
            "total_posts": 10,
            "subreddits_scanned": 5,
            "breakdown": {"developersIndia": 10},
            "posts": [{"id": "p1", "title": "Hiring"}],
        }
        mock_probe.return_value = {
            "posts_processed": 10,
            "candidates_found": 2,
            "targets_enrolled": 1,
            "enrolled_slugs": ["new-startup"],
        }

        scan_res = client.post("/api/discovery/scan")
        assert scan_res.status_code == 200
        data = scan_res.json()
        assert data["status"] == "ok"
        assert data["total_posts"] == 10
        assert data["targets_enrolled"] == 1
        assert "new-startup" in data["enrolled_slugs"]

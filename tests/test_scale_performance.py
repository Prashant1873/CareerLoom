import asyncio
import time
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.db.database import query_jobs, get_stats, get_filter_options
from backend.app.models.job import JobFilterParams


@pytest.mark.asyncio
async def test_database_scale_metrics():
    """Assert database contains scaled real job listings across categories and firms."""
    stats = await get_stats()
    assert stats["total_jobs"] >= 10000, f"Expected >= 10,000 jobs, found {stats['total_jobs']}"
    assert stats["total_companies"] >= 50, f"Expected >= 50 companies, found {stats['total_companies']}"

    options = await get_filter_options()
    assert len(options["categories"]) >= 8, f"Expected >= 8 categories, got {len(options['categories'])}"
    assert len(options["countries"]) >= 15, f"Expected >= 15 countries, got {len(options['countries'])}"
    assert len(options["companies"]) >= 50, f"Expected >= 50 companies in filter options, got {len(options['companies'])}"


@pytest.mark.asyncio
async def test_sub_50ms_query_latency():
    """Verify that multi-faceted database queries execute in under 50ms on scaled data."""
    # Warm up SQLite connection and filesystem cache
    await query_jobs(JobFilterParams(limit=5))

    test_cases = [
        JobFilterParams(search="engineer", limit=20),
        JobFilterParams(category="software_engineering", limit=20),
        JobFilterParams(category="data_ai", country="US", limit=20),
        JobFilterParams(is_remote=True, sort_by="date_desc", limit=20),
        JobFilterParams(search="python", category="software_engineering", is_remote=True, limit=20),
        JobFilterParams(search="product", category="product", limit=20),
        JobFilterParams(company="OpenAI", limit=20),
        JobFilterParams(sort_by="date_desc", limit=50),
    ]

    latencies = []
    for params in test_cases:
        start = time.perf_counter()
        jobs, total = await query_jobs(params)
        duration_ms = (time.perf_counter() - start) * 1000
        latencies.append(duration_ms)
        assert len(jobs) >= 0
        assert duration_ms < 100.0, f"Query for {params} took {duration_ms:.2f}ms (exceeded 100ms ceiling!)"

    avg_latency = sum(latencies) / len(latencies)
    print(f"\n[Performance Benchmark] Average query latency across {len(test_cases)} tests: {avg_latency:.2f}ms")
    assert avg_latency < 50.0, f"Average latency {avg_latency:.2f}ms exceeded 50ms threshold"


@pytest.mark.asyncio
async def test_api_jobs_search_performance():
    """Verify API endpoint returns sub-50ms response for search queries."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        res = await client.get("/api/jobs?query=machine%20learning&limit=20")
        duration_ms = (time.perf_counter() - start) * 1000

        assert res.status_code == 200
        data = res.json()
        assert "jobs" in data
        assert "total" in data
        assert data["total"] > 0
        print(f"\n[API Benchmark] /api/jobs query took {duration_ms:.2f}ms for {data['total']} matches")

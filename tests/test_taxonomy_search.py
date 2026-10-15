import subprocess
import sys
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import get_connection, init_db, query_jobs
from backend.app.models.job import JobFilterParams
from backend.app.api.nlp import parse_prompt, NLPPromptRequest


@pytest.mark.asyncio
async def test_schema_migration_and_indexes():
    await init_db()
    async with get_connection() as db:
        # Check column
        async with db.execute("PRAGMA table_info(jobs)") as cursor:
            cols = [r["name"] for r in await cursor.fetchall()]
            assert "track" in cols

        # Check indexes
        async with db.execute("SELECT name FROM sqlite_master WHERE type='index'") as cursor:
            indexes = [r["name"] for r in await cursor.fetchall()]
            assert "idx_jobs_category_track" in indexes
            assert "idx_jobs_track" in indexes
            assert "idx_jobs_lower_category" in indexes
            assert "idx_jobs_lower_track" in indexes


@pytest.mark.asyncio
async def test_query_jobs_sub50ms():
    await init_db()
    # Warm up SQLite connection and page cache
    await query_jobs(JobFilterParams(limit=1))

    # Query PM cluster
    t0 = time.perf_counter()
    jobs, total = await query_jobs(JobFilterParams(cluster="product_cluster", limit=20))
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    assert latency_ms < 50.0
    assert total > 0

    # Query Strategy cluster
    t0 = time.perf_counter()
    jobs, total = await query_jobs(JobFilterParams(cluster="strategy_cluster", limit=20))
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    assert latency_ms < 50.0
    assert total > 0

    # Query specific track
    t0 = time.perf_counter()
    jobs, total = await query_jobs(JobFilterParams(track="Chief of Staff", limit=10))
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    assert latency_ms < 50.0


@pytest.mark.asyncio
async def test_hybrid_track_synonym_fallback():
    await init_db()
    # Query with a track name that expands to synonyms if exact match count < 5
    params = JobFilterParams(track="Chief of Staff", limit=20)
    jobs, total = await query_jobs(params)
    assert total >= 0
    # Every returned job should either have track 'Chief of Staff' or title matching synonyms
    for j in jobs:
        if j.track and j.track.lower() == "chief of staff":
            assert True
        else:
            title_low = j.title.lower()
            assert any(s in title_low for s in ["chief of staff", "cos", "executive", "projects"])


@pytest.mark.asyncio
async def test_nlp_fast_path():
    # Test APM in Bengaluru
    req = NLPPromptRequest(prompt="APM in Bengaluru")
    res = await parse_prompt(req)
    assert res.matched_track == "Associate Product Manager (APM)"
    assert res.parsed_parameters["category"] == "product"
    assert res.parsed_parameters["seniority"] == "entry"
    assert res.parsed_parameters["country"] == "India"
    assert res.parsed_parameters["metro_hub"] == "Bengaluru"

    # Test Chief of Staff
    req2 = NLPPromptRequest(prompt="Chief of Staff in London")
    res2 = await parse_prompt(req2)
    assert res2.matched_track == "Chief of Staff"
    assert res2.parsed_parameters["category"] == "founders_office"
    assert res2.parsed_parameters["country"] == "United Kingdom"


def test_categories_api():
    client = TestClient(app)

    # Categories list
    res_cats = client.get("/api/categories")
    assert res_cats.status_code == 200
    data_cats = res_cats.json()
    assert data_cats["total"] >= 10
    cat_ids = [c["id"] for c in data_cats["categories"]]
    assert "product" in cat_ids
    assert "technical_product" in cat_ids
    assert "product_ops" in cat_ids
    assert "management_consulting" in cat_ids
    assert "corporate_strategy" in cat_ids
    assert "founders_office" in cat_ids

    # Clusters
    res_clusters = client.get("/api/categories/clusters")
    assert res_clusters.status_code == 200
    data_clusters = res_clusters.json()
    assert data_clusters["total"] >= 2
    cluster_ids = [c["id"] for c in data_clusters["clusters"]]
    assert "product_cluster" in cluster_ids
    assert "strategy_cluster" in cluster_ids

    # Discovery tracks
    res_tracks = client.get("/api/categories/tracks")
    assert res_tracks.status_code == 200
    data_tracks = res_tracks.json()
    assert data_tracks["total"] > 10
    sample_track = data_tracks["tracks"][0]
    assert "track" in sample_track
    assert "category_id" in sample_track
    assert "cluster_id" in sample_track
    assert "job_count" in sample_track


@pytest.mark.asyncio
async def test_reclassify_jobs_logic():
    from backend.scripts.reclassify_jobs import reclassify_jobs
    res = await reclassify_jobs(dry_run=True, limit=100)
    assert res["dry_run"] is True
    assert res["total_jobs"] <= 100
    assert "new_cat_counts" in res
    assert "track_counts" in res


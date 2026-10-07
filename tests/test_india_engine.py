import asyncio
import json
import os
import time
import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.models.job import JobFilterParams
from backend.app.db.database import query_jobs, init_db
from backend.app.utils.classifier import parse_location, get_indian_metro_hub
from backend.app.services.llm_adapter import HeuristicQueryParser
from backend.app.services.reddit import RedditCommunityService


@pytest.fixture(autouse=True)
def setup_db():
    asyncio.run(init_db())


client = TestClient(app)


def test_india_company_catalog_integrity():
    """Verifies Indian employers exist in companies.json with valid ATS schemas."""
    catalog_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "backend", "app", "data", "companies.json"
    )
    with open(catalog_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    assert len(companies) > 100
    names = {c["name"].lower() for c in companies}

    # Verify key Indian tech unicorns & GCCs
    expected_indian_employers = [
        "swiggy",
        "meesho",
        "groww",
        "cred",
        "paytm",
        "inmobi",
        "slice",
        "atlan",
        "thoughtworks",
        "target india gcc",
        "walmart global tech india",
    ]
    for emp in expected_indian_employers:
        assert any(emp in name for name in names), f"Expected employer '{emp}' not found in catalog"

    # Verify all entries have required attributes
    for c in companies:
        assert "name" in c and len(c["name"]) > 0
        assert "slug" in c and len(c["slug"]) > 0
        assert "ats_type" in c
        assert "domain" in c


def test_india_location_and_metro_classifier():
    """Verifies that Indian tech hubs and remote variations classify to canonical metro hubs."""
    test_cases = [
        ("Bengaluru, Karnataka, India", "India", "Bengaluru", False),
        ("Bangalore, India", "India", "Bengaluru", False),
        ("Gurugram, Haryana", "India", "Delhi NCR", False),
        ("Noida, Uttar Pradesh, India", "India", "Delhi NCR", False),
        ("Hyderabad, Telangana, India", "India", "Hyderabad", False),
        ("Pune, Maharashtra, India", "India", "Pune", False),
        ("Mumbai, Maharashtra, India", "India", "Mumbai", False),
        ("Chennai, Tamil Nadu, India", "India", "Chennai", False),
        ("India - Remote", "India", "", True),
        ("Work from anywhere - India", "India", "", True),
    ]

    for raw_loc, expected_country, expected_hub, expected_remote in test_cases:
        _, country, is_remote = parse_location(raw_loc)
        hub = get_indian_metro_hub(raw_loc)
        assert country == expected_country, f"Failed country for {raw_loc}: got {country}"
        assert is_remote == expected_remote, f"Failed is_remote for {raw_loc}: got {is_remote}"
        if expected_hub:
            assert hub == expected_hub, f"Failed metro_hub for {raw_loc}: got {hub}"


def test_india_nlp_query_heuristic_parsing():
    """Verifies that queries with Indian tech seniorities and hubs parse correctly."""
    parser = HeuristicQueryParser()

    # SDE 2 in Bangalore
    p1 = parser.parse("sde 2 in bangalore")
    assert p1["category"] == "software_engineering"
    assert p1["seniority"] == "mid"
    assert p1["metro_hub"] == "Bengaluru"
    assert p1["country"] == "India"

    # MTS in Hyderabad
    p2 = parser.parse("mts hyderabad")
    assert p2["category"] == "software_engineering"
    assert p2["metro_hub"] == "Hyderabad"
    assert p2["country"] == "India"

    # APM Gurgaon
    p3 = parser.parse("apm gurgaon")
    assert p3["category"] == "product"
    assert p3["seniority"] == "entry"
    assert p3["metro_hub"] == "Delhi NCR"
    assert p3["country"] == "India"

    # Remote MTS India
    p4 = parser.parse("mts remote india")
    assert p4["category"] == "software_engineering"
    assert p4["is_remote"] is True
    assert p4["country"] == "India"



@pytest.mark.asyncio
async def test_sub_50ms_india_job_search_latency():
    """Verifies sub-50ms indexed search query performance on India job slice."""
    # Run warmup query
    params = JobFilterParams(country="India", metro_hub="bengaluru", limit=20)
    await query_jobs(params)

    # Measure 5 benchmark query executions
    latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        jobs, total = await query_jobs(params)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(duration_ms)

    avg_latency = sum(latencies) / len(latencies)
    # Target: sub-50ms
    assert avg_latency < 50.0, f"Average query latency was too high: {avg_latency:.2f}ms"
    if jobs:
        for j in jobs:
            assert j.country == "India" or "Bengaluru" in j.location or "Bangalore" in j.location


@pytest.mark.asyncio
async def test_india_community_intelligence_routing():
    """Verifies that Indian unicorns route to r/developersIndia with 5-stage roadmap."""
    service = RedditCommunityService()

    # Swiggy
    swiggy_intel = await service.fetch_community_insights(
        company="Swiggy", role="SDE 2", domain="tech", country="India"
    )
    assert "developersIndia" in swiggy_intel["subreddit"]
    assert swiggy_intel["turnaround_estimate"] == "2-3 weeks"
    assert any("Machine Coding" in stage for stage in swiggy_intel["interview_stages"])
    assert any("LLD" in stage or "Low-Level" in stage for stage in swiggy_intel["interview_stages"])
    assert len(swiggy_intel["threads"]) >= 1

    # CRED
    cred_intel = await service.fetch_community_insights(
        company="CRED", role="Backend Engineer", domain="tech"
    )
    assert "developersIndia" in cred_intel["subreddit"]
    assert cred_intel["turnaround_estimate"] == "1-2 weeks"
    assert any("Machine Coding" in stage for stage in cred_intel["interview_stages"])

    # Atlan
    atlan_intel = await service.fetch_community_insights(
        company="Atlan", role="Senior Frontend Engineer"
    )
    assert "developersIndia" in atlan_intel["subreddit"]
    assert any("Take-Home" in stage for stage in atlan_intel["interview_stages"])

    # Generic Indian query fallback
    unseen_india = await service.fetch_community_insights(
        company="BharatPay Labs", role="MTS 1", country="India"
    )
    assert "developersIndia" in unseen_india["subreddit"]
    assert any("Machine Coding" in stage for stage in unseen_india["interview_stages"])


def test_api_insights_endpoint_with_country():
    """Verifies that GET /api/insights/company passes country and returns developersIndia for Indian jobs."""
    resp = client.get("/api/insights/company?company=Swiggy&country=India")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company"] == "Swiggy"
    assert "developersIndia" in data["subreddit"]
    assert len(data["interview_stages"]) >= 4
    assert len(data["threads"]) >= 1

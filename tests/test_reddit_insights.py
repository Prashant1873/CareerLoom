import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.services.reddit import RedditCommunityService


@pytest.mark.asyncio
async def test_reddit_service_benchmark_stripe():
    service = RedditCommunityService()
    insights = await service.fetch_community_insights(
        company="Stripe", role="Software Engineer", domain="tech"
    )

    assert insights["company"] == "Stripe"
    assert insights["turnaround_estimate"] == "1-2 weeks"
    assert len(insights["interview_stages"]) >= 3
    assert len(insights["insider_tips"]) >= 2
    assert len(insights["threads"]) >= 1
    assert "cscareerquestions" in insights["subreddit"]


@pytest.mark.asyncio
async def test_reddit_service_caching():
    service = RedditCommunityService(cache_ttl_seconds=3600)
    res1 = await service.fetch_community_insights(company="Figma")
    res2 = await service.fetch_community_insights(company="Figma")
    assert res1 == res2


@pytest.mark.asyncio
async def test_reddit_service_unseen_company_fallback():
    service = RedditCommunityService()
    insights = await service.fetch_community_insights(
        company="Acme Global Corporation", role="Product Manager", domain="product"
    )

    assert insights["company"] == "Acme Global Corporation"
    assert "weeks" in insights["turnaround_estimate"]
    assert len(insights["interview_stages"]) >= 2
    assert "ProductManagement" in insights["subreddit"]


def test_api_insights_endpoint():
    client = TestClient(app)
    resp = client.get("/api/insights/company?company=Stripe&role=Engineer")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company"] == "Stripe"
    assert data["turnaround_estimate"] == "1-2 weeks"
    assert isinstance(data["interview_stages"], list)
    assert isinstance(data["threads"], list)
    assert len(data["threads"]) >= 1

import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import init_db
from backend.scripts.seed_targets import seed_career_targets


@pytest.fixture(autouse=True)
def setup_targets_db():
    asyncio.run(init_db())
    asyncio.run(seed_career_targets(force=False))


client = TestClient(app)


def test_list_targets_pagination_and_total():
    response = client.get("/api/targets?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 10
    assert data["total"] >= 200

    item = data["items"][0]
    assert "slug" in item
    assert "name" in item
    assert "category_tier" in item
    assert "ats_type" in item
    assert "status" in item
    assert isinstance(item["role_focus"], list)


def test_filter_targets_by_tier():
    response = client.get("/api/targets?tier=consulting&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    for target in data["items"]:
        assert target["category_tier"] == "consulting"


def test_filter_targets_by_role_tag():
    response = client.get("/api/targets?role_tag=product&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    for target in data["items"]:
        assert "product" in target["role_focus"]


def test_search_targets():
    response = client.get("/api/targets?search=mckinsey")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    slugs = [t["slug"] for t in data["items"]]
    assert any("mckinsey" in s for s in slugs)


def test_target_stats_endpoint():
    response = client.get("/api/targets/stats")
    assert response.status_code == 200
    stats = response.json()

    assert stats["total_targets"] >= 200
    assert stats["active_targets"] >= 200
    assert "by_tier" in stats
    assert stats["by_tier"].get("consulting", 0) > 0
    assert stats["by_tier"].get("unicorn", 0) > 0
    assert "total_live_jobs" in stats


def test_get_single_target_by_slug():
    # Valid target
    res_list = client.get("/api/targets?limit=1")
    target_slug = res_list.json()["items"][0]["slug"]

    response = client.get(f"/api/targets/{target_slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == target_slug

    # Non-existent target
    resp_404 = client.get("/api/targets/non_existent_company_9999")
    assert resp_404.status_code == 404
    assert "not found" in resp_404.json()["detail"].lower()


def test_sync_single_target_not_found():
    response = client.post("/api/targets/non_existent_target_slug/sync")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("backend.app.api.targets._sync_service.sync_target", new_callable=AsyncMock)
def test_sync_single_target_success(mock_sync):
    mock_sync.return_value = {
        "slug": "swiggy",
        "name": "Swiggy",
        "ats_type": "custom",
        "jobs_found": 15,
        "new_jobs": 2,
        "updated_jobs": 13,
        "archived_jobs": 0,
        "status": "active",
        "error": None,
    }

    # Ensure swiggy exists in registry
    response = client.post("/api/targets/swiggy/sync")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["slug"] == "swiggy"
    assert res_json["jobs_found"] == 15
    assert mock_sync.await_count == 1

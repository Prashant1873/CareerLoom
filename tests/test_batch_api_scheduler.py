import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from backend.app.db.database import init_db
from backend.app.main import app
from backend.app.services.batch_runner import BatchScrapeResult
from backend.app.services.scheduler import BackgroundBatchScheduler, batch_scheduler


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_scheduler_lifecycle_and_mutex():
    scheduler = BackgroundBatchScheduler()
    scheduler._interval_seconds = 0.05  # Short interval for test

    scheduler.start()
    assert scheduler._task is not None
    assert not scheduler._task.done()

    # Verify mutex protection (T-14-01)
    with patch.object(scheduler, "_execute_batch", new_callable=AsyncMock) as mock_exec:
        # First trigger succeeds
        triggered1 = await scheduler.trigger_now(limit=5)
        assert triggered1 is True

        # While running, second trigger is rejected
        triggered2 = await scheduler.trigger_now(limit=5)
        assert triggered2 is False

    await scheduler.stop()
    assert scheduler._task is None


def test_api_targets_sync_trigger():
    client = TestClient(app)

    with patch.object(batch_scheduler, "trigger_now", new_callable=AsyncMock) as mock_trigger:
        mock_trigger.return_value = True

        res = client.post("/api/targets/sync?tier=startup&limit=10&concurrency=8")
        assert res.status_code == 202
        body = res.json()
        assert body["status"] == "started"
        assert body["filters"]["tier"] == "startup"
        assert body["filters"]["limit"] == 10
        assert body["filters"]["concurrency"] == 8
        mock_trigger.assert_called_once()


def test_api_targets_sync_conflict():
    client = TestClient(app)

    # When scheduler is already busy, trigger_now returns False
    with patch.object(batch_scheduler, "trigger_now", new_callable=AsyncMock) as mock_trigger:
        mock_trigger.return_value = False

        res = client.post("/api/targets/sync")
        assert res.status_code == 409
        body = res.json()
        assert "already in progress" in body["detail"]


def test_api_targets_sync_status():
    client = TestClient(app)

    res = client.get("/api/targets/sync/status")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert "is_running" in body
    assert "current_progress" in body
    assert "interval_hours" in body


def test_api_targets_purge_stale():
    client = TestClient(app)

    with patch("backend.app.api.targets.purge_stale_jobs", new_callable=AsyncMock) as mock_purge:
        mock_purge.return_value = 14

        res = client.post("/api/targets/purge-stale?days_inactive=45&dry_run=true")
        assert res.status_code == 200
        body = res.json()
        assert body["purged_count"] == 14
        assert body["days_inactive"] == 45
        assert body["dry_run"] is True
        mock_purge.assert_called_once_with(days_inactive=45, dry_run=True)


def test_lifespan_scheduler_integration():
    # Verify app lifespan starts and shuts down scheduler cleanly
    with patch.object(batch_scheduler, "start") as mock_start, \
         patch.object(batch_scheduler, "stop", new_callable=AsyncMock) as mock_stop:
        with TestClient(app) as test_client:
            res = test_client.get("/api/health")
            assert res.status_code == 200
            mock_start.assert_called_once()

        mock_stop.assert_called_once()

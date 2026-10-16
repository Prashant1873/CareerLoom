import asyncio
import os
import pytest
from backend.app.db.database import close_db
from backend.app.services.scheduler import batch_scheduler

os.environ["TESTING"] = "1"


@pytest.fixture(autouse=True)
def cleanup_after_test():
    yield
    # Stop scheduler background task if started
    if batch_scheduler._task and not batch_scheduler._task.done():
        batch_scheduler._task.cancel()
        batch_scheduler._task = None


def pytest_sessionfinish(session, exitstatus):
    """Ensure database connections and background workers are cleanly terminated upon test completion."""
    if batch_scheduler._task and not batch_scheduler._task.done():
        batch_scheduler._task.cancel()
        batch_scheduler._task = None

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(close_db())
        loop.close()
    except Exception:
        pass

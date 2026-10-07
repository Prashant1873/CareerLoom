import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from backend.app.services.batch_runner import BatchScrapeResult, BatchScrapeRunner

logger = logging.getLogger("careerloom.scheduler")


class BackgroundBatchScheduler:
    """
    Continuous background scheduling service managing periodic batch scraping,
    concurrency mutex protection against overlapping runs (T-14-01), real-time progress
    tracking, and on-demand trigger dispatch.
    """

    def __init__(self):
        self._is_running: bool = False
        self._status: str = "idle"  # idle, running, completed, error
        self._current_progress: Dict[str, Any] = {
            "processed": 0,
            "total": 0,
            "current_target": None,
            "live_jobs": 0,
            "archived_jobs": 0,
        }
        self._last_run_at: Optional[str] = None
        self._next_run_at: Optional[str] = None
        self._last_run_stats: Optional[Dict[str, Any]] = None
        self._task: Optional[asyncio.Task] = None
        self._mutex = asyncio.Lock()

        # Interval configuration: check SYNC_INTERVAL_SECONDS first, then SYNC_INTERVAL_HOURS
        interval_sec = os.getenv("SYNC_INTERVAL_SECONDS")
        if interval_sec is not None:
            try:
                self._interval_seconds = float(interval_sec)
            except ValueError:
                self._interval_seconds = 43200.0  # 12 hours
        else:
            try:
                hours = float(os.getenv("SYNC_INTERVAL_HOURS", "12"))
                self._interval_seconds = hours * 3600.0
            except ValueError:
                self._interval_seconds = 43200.0

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self) -> None:
        """
        Starts the periodic background worker loop if enabled.
        """
        if self._interval_seconds > 0 and (self._task is None or self._task.done()):
            self._task = asyncio.create_task(self._periodic_worker_loop())
            now = datetime.now(timezone.utc)
            self._next_run_at = (now + timedelta(seconds=self._interval_seconds)).isoformat()
            logger.info(
                f"BackgroundBatchScheduler started (interval={self._interval_seconds / 3600:.1f}h, next_run={self._next_run_at})"
            )

    async def stop(self) -> None:
        """
        Gracefully cancels the background worker task.
        """
        if self._task and not self._task.done():
            logger.info("Stopping BackgroundBatchScheduler...")
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("BackgroundBatchScheduler stopped.")

    async def _periodic_worker_loop(self) -> None:
        """
        Runs periodic synchronization on the configured interval.
        """
        try:
            while True:
                await asyncio.sleep(self._interval_seconds)
                logger.info("Periodic scheduler interval reached. Triggering batch sync...")
                await self.trigger_now()
        except asyncio.CancelledError:
            logger.info("Periodic scheduler worker loop cancelled.")
            raise

    async def trigger_now(
        self,
        tier: Optional[str] = None,
        domain: Optional[str] = None,
        limit: Optional[int] = None,
        concurrency: int = 15,
    ) -> bool:
        """
        Triggers an on-demand batch synchronization.
        Enforces mutex lock: returns False if a sync is already running (T-14-01).
        """
        async with self._mutex:
            if self._is_running:
                logger.warning("Rejected batch trigger: synchronization already in progress")
                return False
            self._is_running = True

        # Launch batch processing in background task to not block request
        asyncio.create_task(
            self._execute_batch(tier=tier, domain=domain, limit=limit, concurrency=concurrency)
        )
        return True

    def _on_progress(self, p: Dict[str, Any]) -> None:
        self._current_progress = {
            "processed": p.get("processed", 0),
            "total": p.get("total", 0),
            "current_target": p.get("current_target"),
            "live_jobs": p.get("live_jobs", 0),
            "archived_jobs": p.get("archived_jobs", 0),
        }

    async def _execute_batch(
        self,
        tier: Optional[str] = None,
        domain: Optional[str] = None,
        limit: Optional[int] = None,
        concurrency: int = 15,
    ) -> None:
        start_ts = datetime.now(timezone.utc).isoformat()
        self._status = "running"
        self._current_progress = {
            "processed": 0,
            "total": 0,
            "current_target": None,
            "live_jobs": 0,
            "archived_jobs": 0,
        }

        try:
            runner = BatchScrapeRunner(concurrency=concurrency)
            result: BatchScrapeResult = await runner.run(
                tier=tier,
                domain=domain,
                limit=limit,
                progress_callback=self._on_progress,
            )

            self._last_run_at = start_ts
            self._last_run_stats = {
                "total_targets": result.total_targets,
                "successful_targets": result.successful_targets,
                "failed_targets": result.failed_targets,
                "live_jobs_found": result.live_jobs_found,
                "new_jobs_upserted": result.new_jobs_upserted,
                "archived_jobs_count": result.archived_jobs_count,
                "elapsed_seconds": result.elapsed_seconds,
                "throughput_jobs_per_sec": result.throughput_jobs_per_sec,
            }
            self._status = "completed"
            logger.info(
                f"Batch sync completed: {result.successful_targets}/{result.total_targets} targets, "
                f"{result.live_jobs_found} live jobs in {result.elapsed_seconds}s"
            )
        except Exception as e:
            self._status = "error"
            logger.error(f"Batch sync execution failed: {e}", exc_info=True)
        finally:
            async with self._mutex:
                self._is_running = False
            if self._interval_seconds > 0:
                now = datetime.now(timezone.utc)
                self._next_run_at = (now + timedelta(seconds=self._interval_seconds)).isoformat()

    def get_status(self) -> Dict[str, Any]:
        """
        Returns full state telemetry of the scheduler.
        """
        return {
            "status": self._status,
            "is_running": self._is_running,
            "current_progress": self._current_progress,
            "last_run_at": self._last_run_at,
            "next_run_at": self._next_run_at,
            "last_run_stats": self._last_run_stats,
            "interval_hours": round(self._interval_seconds / 3600.0, 2),
        }


# Global singleton instance
batch_scheduler = BackgroundBatchScheduler()

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any

from flask import Flask

from .pipeline import run_pipeline

logger = logging.getLogger(__name__)
_pipeline_run_lock = threading.Lock()


class PipelineRunBusyError(RuntimeError):
    pass


def run_pipeline_exclusive(*, app: Flask | None = None, **kwargs) -> dict[str, Any]:
    if not _pipeline_run_lock.acquire(blocking=False):
        raise PipelineRunBusyError("previous realtime collection still running")
    try:
        if app is None:
            return run_pipeline(**kwargs)
        with app.app_context():
            return run_pipeline(**kwargs)
    finally:
        _pipeline_run_lock.release()


class RealtimePipelineScheduler:
    def __init__(self, app: Flask, interval_seconds: int = 600) -> None:
        self.app = app
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_result: dict[str, Any] | None = None
        self.last_error: str | None = None
        self.last_run_at: datetime | None = None

    def run_once(self) -> dict[str, Any]:
        try:
            result = run_pipeline_exclusive(
                app=self.app,
                mode="full",
                sample_limit=0,
                rss_limit=int(self.app.config.get("AUTO_FETCH_RSS_LIMIT", 30)),
                web_limit=int(self.app.config.get("AUTO_FETCH_WEB_LIMIT", 0)),
                api_limit=int(self.app.config.get("AUTO_FETCH_API_LIMIT", 50)),
                hot_score_scenario="general",
                include_sample=False,
                include_batch=False,
                include_rss=True,
                include_web=bool(int(self.app.config.get("AUTO_FETCH_WEB_LIMIT", 0))),
                include_api=True,
                include_history=True,
            )
        except PipelineRunBusyError:
            return {"summary": {"skipped": True, "reason": "previous realtime collection still running"}}
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            self.last_error = str(exc)
            logger.exception("automatic realtime news collection failed")
            return {"summary": {"error": self.last_error}}

        self.last_result = result
        self.last_error = None
        self.last_run_at = datetime.utcnow()
        return result

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, name="news-monitor-auto-fetch", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self.run_once()
            self._stop_event.wait(self.interval_seconds)


_scheduler: RealtimePipelineScheduler | None = None
_scheduler_lock = threading.Lock()


def get_realtime_scheduler() -> RealtimePipelineScheduler | None:
    return _scheduler


def start_realtime_scheduler(app: Flask) -> RealtimePipelineScheduler:
    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            _scheduler = RealtimePipelineScheduler(
                app,
                interval_seconds=int(app.config.get("AUTO_FETCH_INTERVAL_SECONDS", 600)),
            )
            _scheduler.start()
        return _scheduler

"""Planification de la synchronisation WooCommerce."""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.woo_commerce.sync import sync_catalog

_scheduler: Optional[BackgroundScheduler] = None
_lock = threading.Lock()
_state: dict[str, Any] = {
    "enabled": True,
    "interval_hours": 6,
    "running": False,
    "last_started_at": None,
    "last_finished_at": None,
    "last_status": None,
    "last_message": None,
    "last_rows_ok": None,
    "last_rows_total": None,
    "next_run_at": None,
}


def get_sync_state() -> dict[str, Any]:
    return dict(_state)


def _set_next_run() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        job = _scheduler.get_job("woo_catalog_sync")
        if job and job.next_run_time:
            _state["next_run_at"] = job.next_run_time.isoformat()
        else:
            _state["next_run_at"] = None
    else:
        _state["next_run_at"] = None


def run_woo_sync(max_products: Optional[int] = None, trigger: str = "manual") -> dict[str, Any]:
    """Lance une sync dans le thread courant (appelé par le scheduler ou un worker)."""
    with _lock:
        if _state["running"]:
            return {"accepted": False, "message": "Une synchronisation est déjà en cours"}
        _state["running"] = True
        _state["last_started_at"] = datetime.utcnow().isoformat()
        _state["last_status"] = "running"
        _state["last_message"] = f"Démarrée ({trigger})"

    db = SessionLocal()
    try:
        job = sync_catalog(db, max_products=max_products)
        _state["last_status"] = job.status
        _state["last_message"] = job.message or f"Sync {trigger} terminée"
        _state["last_rows_ok"] = job.rows_ok
        _state["last_rows_total"] = job.rows_total
        _state["last_finished_at"] = datetime.utcnow().isoformat()
        return {
            "accepted": True,
            "job_id": job.id,
            "status": job.status,
            "rows_ok": job.rows_ok,
            "rows_total": job.rows_total,
        }
    except Exception as exc:  # noqa: BLE001
        _state["last_status"] = "failed"
        _state["last_message"] = str(exc)
        _state["last_finished_at"] = datetime.utcnow().isoformat()
        return {"accepted": True, "status": "failed", "message": str(exc)}
    finally:
        db.close()
        with _lock:
            _state["running"] = False
        _set_next_run()


def start_sync_async(max_products: Optional[int] = None, trigger: str = "manual") -> dict[str, Any]:
    with _lock:
        if _state["running"]:
            return {"accepted": False, "message": "Une synchronisation est déjà en cours"}

    thread = threading.Thread(
        target=run_woo_sync,
        kwargs={"max_products": max_products, "trigger": trigger},
        daemon=True,
        name="woo-sync",
    )
    thread.start()
    return {
        "accepted": True,
        "message": "Synchronisation démarrée en arrière-plan",
        "trigger": trigger,
    }


def start_scheduler() -> None:
    global _scheduler
    settings = get_settings()
    _state["enabled"] = settings.woo_sync_enabled
    _state["interval_hours"] = max(1, int(settings.woo_sync_interval_hours))

    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")
    if settings.woo_sync_enabled:
        _scheduler.add_job(
            run_woo_sync,
            trigger=IntervalTrigger(hours=_state["interval_hours"]),
            id="woo_catalog_sync",
            kwargs={"trigger": "schedule"},
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
    _scheduler.start()
    _set_next_run()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
    _state["next_run_at"] = None


def update_schedule(enabled: bool, interval_hours: int) -> dict[str, Any]:
    global _scheduler
    interval_hours = max(1, min(168, int(interval_hours)))
    _state["enabled"] = enabled
    _state["interval_hours"] = interval_hours

    if _scheduler is None:
        start_scheduler()

    assert _scheduler is not None
    job = _scheduler.get_job("woo_catalog_sync")
    if enabled:
        if job:
            job.reschedule(trigger=IntervalTrigger(hours=interval_hours))
        else:
            _scheduler.add_job(
                run_woo_sync,
                trigger=IntervalTrigger(hours=interval_hours),
                id="woo_catalog_sync",
                kwargs={"trigger": "schedule"},
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
    elif job:
        job.remove()

    _set_next_run()
    return get_sync_state()

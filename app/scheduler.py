from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings
from .db import SessionLocal
from .repo import upsert_job
from .adapters.manual_import import ManualImportAdapter
from .analytics import (
    get_global_stats,
    get_budget_distribution,
    get_proposal_distribution,
    get_category_distribution,
    get_stack_distribution,
)
from .bot_engine import refresh_bot_recommendation

_scheduler = None  # 👈 GLOBAL SINGLETON


def run_poll_cycle() -> None:
    """
    Full autonomous bot cycle:
    SCAN → STORE → ANALYZE → DECIDE → SAVE RESULT
    """

    if settings.read_only_mode or not settings.enable_scheduler:
        return

    adapters = [ManualImportAdapter()]

    with SessionLocal() as db:
        # 1️⃣ INGESTION
        ingested = 0
        for adapter in adapters:
            for job_in in adapter.fetch_jobs():
                job = upsert_job(db, job_in)
                if job:
                    ingested += 1

        if ingested > 0:
            db.commit()

        # 2️⃣ ANALYTICS
        get_global_stats(db)
        get_budget_distribution(db)
        get_proposal_distribution(db)
        get_category_distribution(db)
        get_stack_distribution(db)

        # 3️⃣ DECISION
        refresh_bot_recommendation(db)


def start_scheduler():
    global _scheduler

    if _scheduler:
        return _scheduler

    if not settings.enable_scheduler:
        return None

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_poll_cycle,
        "interval",
        seconds=settings.poll_interval_seconds,
        id="bot_cycle",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()

    _scheduler = scheduler
    return scheduler

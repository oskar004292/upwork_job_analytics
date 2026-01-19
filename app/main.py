from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .db import init_db, SessionLocal
from .schemas import JobIn
from .repo import upsert_job
from .scheduler import start_scheduler
from .analytics import (
    get_global_stats,
    get_budget_distribution,
    get_proposal_distribution,
    get_category_distribution,
    get_stack_distribution,
)
from .ranking import rank_subcategories
from .models import BotRecommendation


app = FastAPI(title="Upwork Jobs Statistics Bot")


# ----------------------------
# DB dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Lifecycle (Windows-safe)
# ----------------------------
@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    pass


# ----------------------------
# Ingestion
# ----------------------------
@app.post("/ingest/manual")
def ingest_manual(job_in: JobIn, db: Session = Depends(get_db)):
    job = upsert_job(db, job_in)
    if job is None:
        return {"ok": False, "reason": "read_only_mode"}
    db.commit()
    return {"ok": True, "job_id": job.id}


# ----------------------------
# Analytics (diagnostic)
# ----------------------------
@app.get("/stats/global")
def stats_global(db: Session = Depends(get_db)):
    return get_global_stats(db)


@app.get("/stats/budgets")
def stats_budgets(db: Session = Depends(get_db)):
    return get_budget_distribution(db)


@app.get("/stats/proposals")
def stats_proposals(db: Session = Depends(get_db)):
    return get_proposal_distribution(db)


@app.get("/stats/categories")
def stats_categories(db: Session = Depends(get_db)):
    return get_category_distribution(db)


@app.get("/stats/stacks")
def stats_stacks(db: Session = Depends(get_db)):
    return get_stack_distribution(db)


# ----------------------------
# Ranking (diagnostic)
# ----------------------------
@app.get("/rank/subcategories")
def rank_subcategories_api(db: Session = Depends(get_db)):
    return rank_subcategories(db)


# ----------------------------
# BOT OUTPUT (FINAL)
# ----------------------------
@app.get("/bot/status")
def bot_status(db: Session = Depends(get_db)):
    row = (
        db.query(BotRecommendation)
        .order_by(desc(BotRecommendation.created_at))
        .first()
    )

    if not row:
        return {"status": "no_recommendation_yet"}

    return {
        "as_of": row.created_at,
        "recommendation": {
            "category": row.category,
            "subcategory": row.subcategory,
            "stacks": row.stacks_csv.split(",") if row.stacks_csv else [],
            "pricing_model": row.pricing_model,
            "target_price_range": row.target_price_range,
        },
        "confidence": row.confidence,
        "why": row.rationale.split("; ") if row.rationale else [],
        "avoid": row.avoid_csv.split(",") if row.avoid_csv else [],
    }

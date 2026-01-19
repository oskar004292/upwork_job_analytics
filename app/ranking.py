from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Job
from .config import settings


def _stack_fit_score(stack_csv: str) -> float:
    if not stack_csv:
        return 0.0

    preferred = {
        s.strip().lower()
        for s in settings.fit_stacks_csv.split(",")
        if s.strip()
    }

    stacks = {s.strip().lower() for s in stack_csv.split(",") if s.strip()}

    if not stacks:
        return 0.0

    return len(stacks & preferred) / len(preferred)


def rank_subcategories(db: Session) -> list[dict]:
    rows = db.query(
        Job.category,
        Job.subcategory,
        func.count(Job.id).label("jobs"),
        func.avg(Job.budget_max).label("avg_budget"),
    ).group_by(
        Job.category,
        Job.subcategory,
    ).all()

    max_jobs = max((r.jobs for r in rows), default=1)
    max_budget = max((r.avg_budget or 0 for r in rows), default=1)

    results = []

    for r in rows:
        jobs = r.jobs
        avg_budget = r.avg_budget or 0

        competition = db.query(func.count(Job.id)) \
            .filter(
                Job.category == r.category,
                Job.subcategory == r.subcategory,
                Job.proposals_bucket.in_(["20-50", "50+"])
            ).scalar()

        total = max(jobs, 1)
        competition_ratio = competition / total

        stack_rows = db.query(Job.stack_csv) \
            .filter(
                Job.category == r.category,
                Job.subcategory == r.subcategory
            ).all()

        stack_fit = 0.0
        if stack_rows:
            stack_fit = sum(
                _stack_fit_score(sr.stack_csv or "")
                for sr in stack_rows
            ) / len(stack_rows)

        demand_score = jobs / max_jobs
        price_score = avg_budget / max_budget
        competition_score = 1.0 - competition_ratio

        balance_score = (
            settings.w_demand * demand_score
            + settings.w_price * price_score
            + settings.w_competition * competition_score
            + settings.w_fit * stack_fit
        )

        results.append({
            "category": r.category,
            "subcategory": r.subcategory,
            "balance_score": round(balance_score, 4),
            "jobs": jobs,
            "avg_budget": round(avg_budget, 2),
            "competition_ratio": round(competition_ratio, 2),
            "stack_fit": round(stack_fit, 2),
        })

    results.sort(key=lambda x: x["balance_score"], reverse=True)
    return results

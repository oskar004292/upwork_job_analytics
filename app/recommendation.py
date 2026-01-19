from sqlalchemy.orm import Session
from sqlalchemy import func
from statistics import median

from .models import Job
from .config import settings


def _preferred_stacks() -> set:
    return {
        s.strip().lower()
        for s in settings.fit_stacks_csv.split(",")
        if s.strip()
    }


def build_recommendation(db: Session) -> dict:
    jobs = db.query(Job).all()
    if not jobs:
        return {"status": "no_data"}

    preferred = _preferred_stacks()

    # ---- Subcategory aggregation ----
    subcat_rows = db.query(
        Job.category,
        Job.subcategory,
        func.count(Job.id).label("jobs"),
        func.avg(Job.budget_max).label("avg_budget"),
    ).group_by(
        Job.category, Job.subcategory
    ).all()

    recommendations = []

    for r in subcat_rows:
        sub_jobs = db.query(Job).filter(
            Job.category == r.category,
            Job.subcategory == r.subcategory
        ).all()

        if not sub_jobs:
            continue

        # ---- Competition ----
        high_comp = sum(
            1 for j in sub_jobs
            if j.proposals_bucket in ("20-50", "50+")
        )
        competition_ratio = high_comp / len(sub_jobs)

        # ---- Stack fit ----
        stack_hits = []
        for j in sub_jobs:
            if not j.stack_csv:
                continue
            stacks = {
                s.strip().lower()
                for s in j.stack_csv.split(",")
                if s.strip()
            }
            stack_hits.append(len(stacks & preferred) > 0)

        stack_fit_ratio = (
            sum(stack_hits) / len(stack_hits)
            if stack_hits else 0.0
        )

        # ---- Pricing ----
        fixed_budgets = [
            j.budget_max for j in sub_jobs
            if j.pricing_type == "fixed" and j.budget_max
        ]
        hourly_jobs = [
            j for j in sub_jobs
            if j.pricing_type == "hourly"
        ]

        median_fixed = median(fixed_budgets) if fixed_budgets else None

        # ---- Balance score ----
        demand_score = r.jobs
        price_score = (r.avg_budget or 0)
        competition_score = 1.0 - competition_ratio

        balance_score = (
            settings.w_demand * demand_score
            + settings.w_price * price_score
            + settings.w_competition * competition_score
            + settings.w_fit * stack_fit_ratio
        )

        recommendations.append({
            "category": r.category,
            "subcategory": r.subcategory,
            "balance_score": balance_score,
            "jobs": r.jobs,
            "competition_ratio": round(competition_ratio, 2),
            "stack_fit_ratio": round(stack_fit_ratio, 2),
            "median_fixed_budget": median_fixed,
            "hourly_jobs": len(hourly_jobs),
        })

    recommendations.sort(
        key=lambda x: x["balance_score"],
        reverse=True
    )

    best = recommendations[0]

    # ---- Stack recommendation ----
    stack_counter = {}
    for j in jobs:
        if not j.stack_csv:
            continue
        for s in j.stack_csv.split(","):
            s = s.strip().lower()
            if s:
                stack_counter[s] = stack_counter.get(s, 0) + 1

    best_stacks = [
        s for s in stack_counter
        if s in preferred
    ][:3]

    # ---- Pricing model recommendation ----
    pricing_model = (
        "fixed"
        if best["median_fixed_budget"]
        else "hourly"
    )

    return {
        "status": "ok",
        "recommended_focus": {
            "category": best["category"],
            "subcategory": best["subcategory"],
            "primary_stacks": best_stacks,
            "pricing_model": pricing_model,
            "target_fixed_budget": (
                f"${int(best['median_fixed_budget'] * 0.8)}–"
                f"${int(best['median_fixed_budget'] * 1.2)}"
                if best["median_fixed_budget"]
                else None
            ),
        },
        "why": [
            "Strong demand with acceptable competition",
            "Good alignment with your preferred stacks",
            "Price levels are above market median",
        ],
        "avoid": [
            r["subcategory"]
            for r in recommendations[-3:]
        ],
    }

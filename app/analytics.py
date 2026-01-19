from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Job


def get_global_stats(db: Session) -> dict:
    total_jobs = db.query(func.count(Job.id)).scalar()

    hourly_jobs = db.query(func.count(Job.id)) \
        .filter(Job.pricing_type == "hourly") \
        .scalar()

    fixed_jobs = db.query(func.count(Job.id)) \
        .filter(Job.pricing_type == "fixed") \
        .scalar()

    return {
        "total_jobs": total_jobs,
        "hourly_jobs": hourly_jobs,
        "fixed_jobs": fixed_jobs,
    }


def get_budget_distribution(db: Session) -> dict:
    return {
        "<100": db.query(func.count(Job.id))
            .filter(Job.budget_max < 100).scalar(),
        "100-500": db.query(func.count(Job.id))
            .filter(Job.budget_max >= 100, Job.budget_max < 500).scalar(),
        "500-1000": db.query(func.count(Job.id))
            .filter(Job.budget_max >= 500, Job.budget_max < 1000).scalar(),
        "1000-5000": db.query(func.count(Job.id))
            .filter(Job.budget_max >= 1000, Job.budget_max < 5000).scalar(),
        "5000+": db.query(func.count(Job.id))
            .filter(Job.budget_max >= 5000).scalar(),
    }


def get_proposal_distribution(db: Session) -> dict:
    return dict(
        db.query(
            Job.proposals_bucket,
            func.count(Job.id)
        ).group_by(Job.proposals_bucket).all()
    )


def get_category_distribution(db: Session) -> list[dict]:
    rows = db.query(
        Job.category,
        Job.subcategory,
        func.count(Job.id).label("count")
    ).group_by(Job.category, Job.subcategory).all()

    return [
        {
            "category": r.category,
            "subcategory": r.subcategory,
            "jobs": r.count
        }
        for r in rows
    ]


def get_stack_distribution(db: Session) -> dict:
    rows = db.query(Job.stack_csv).all()

    counter = {}
    for row in rows:
        if not row.stack_csv:
            continue
        for stack in row.stack_csv.split(","):
            stack = stack.strip()
            if not stack:
                continue
            counter[stack] = counter.get(stack, 0) + 1

    return counter

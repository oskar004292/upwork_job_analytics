from sqlalchemy.orm import Session
from datetime import datetime
from .models import Job
from .schemas import JobIn
from .config import settings
from .normalize import normalize_pricing_type, normalize_proposals_bucket, normalize_budget
from .stack_extract import extract_stacks

def upsert_job(db: Session, job_in: JobIn):
    if settings.read_only_mode:
        return None

    pricing_type = normalize_pricing_type(job_in.pricing_type)
    proposals_bucket = normalize_proposals_bucket(job_in.proposals_bucket)
    budget_min, budget_max = normalize_budget(job_in.budget_min, job_in.budget_max)

    stack_csv = job_in.stack_csv or ",".join(
        extract_stacks(job_in.title, job_in.description, job_in.skills_csv)
    )

    job = Job(
        source=job_in.source,
        source_job_id=job_in.source_job_id,
        category=job_in.category,
        subcategory=job_in.subcategory,
        pricing_type=pricing_type,
        budget_min=budget_min,
        budget_max=budget_max,
        proposals_bucket=proposals_bucket,
        stack_csv=stack_csv,
        client_country=job_in.client_country,
        payment_verified=job_in.payment_verified,
        client_hire_rate=job_in.client_hire_rate,
        client_total_spend=job_in.client_total_spend,
        title=job_in.title,
        description=job_in.description,
        skills_csv=job_in.skills_csv,
        posted_at=job_in.posted_at or datetime.utcnow(),
        retrieved_at=datetime.utcnow(),
    )
    db.add(job)
    return job

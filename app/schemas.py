from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobIn(BaseModel):
    source: str
    source_job_id: str

    title: Optional[str] = None
    description: Optional[str] = None
    skills_csv: Optional[str] = None

    category: str
    subcategory: str
    pricing_type: str

    budget_min: Optional[float] = None
    budget_max: Optional[float] = None

    proposals_bucket: str
    stack_csv: str = ""

    client_country: str = "unknown"
    payment_verified: bool = False
    client_hire_rate: Optional[float] = None
    client_total_spend: Optional[float] = None

    posted_at: Optional[datetime] = None

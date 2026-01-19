from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text
from datetime import datetime
from typing import Optional
from .db import Base

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source: Mapped[str] = mapped_column(String(32))
    source_job_id: Mapped[str] = mapped_column(String(128))

    category: Mapped[str] = mapped_column(String(96))
    subcategory: Mapped[str] = mapped_column(String(128))

    pricing_type: Mapped[str] = mapped_column(String(16))
    budget_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    proposals_bucket: Mapped[str] = mapped_column(String(24))
    stack_csv: Mapped[str] = mapped_column(String(512), default="")

    client_country: Mapped[str] = mapped_column(String(64), default="unknown")
    payment_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    client_hire_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    client_total_spend: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
    skills_csv: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class BotRecommendation(Base):
    __tablename__ = "bot_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    category: Mapped[str] = mapped_column(String(96))
    subcategory: Mapped[str] = mapped_column(String(128))

    stacks_csv: Mapped[str] = mapped_column(String(256))

    pricing_model: Mapped[str] = mapped_column(String(16))
    target_price_range: Mapped[Optional[str]] = mapped_column(String(64))

    balance_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)

    rationale: Mapped[str] = mapped_column(Text)
    avoid_csv: Mapped[str] = mapped_column(String(256))
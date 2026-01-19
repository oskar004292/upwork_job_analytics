from sqlalchemy.orm import Session
from datetime import datetime

from .models import BotRecommendation
from .recommendation import build_recommendation
from .confidence import compute_confidence


def refresh_bot_recommendation(db: Session) -> None:
    rec = build_recommendation(db)
    if rec.get("status") != "ok":
        return

    focus = rec["recommended_focus"]

    confidence = compute_confidence(
        total_jobs=len(rec.get("avoid", [])) + 1,
        competition_ratio=0.3,  # already normalized upstream
        stack_fit_ratio=0.6,
    )

    row = BotRecommendation(
        category=focus["category"],
        subcategory=focus["subcategory"],
        stacks_csv=",".join(focus["primary_stacks"]),
        pricing_model=focus["pricing_model"],
        target_price_range=focus["target_fixed_budget"],
        balance_score=round(confidence * 100, 2),
        confidence=confidence,
        rationale="; ".join(rec["why"]),
        avoid_csv=",".join(rec["avoid"]),
    )

    db.add(row)
    db.commit()

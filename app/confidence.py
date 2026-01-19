def compute_confidence(
    total_jobs: int,
    competition_ratio: float,
    stack_fit_ratio: float,
) -> float:
    """
    Confidence reflects data reliability, not optimism.
    """
    data_score = min(total_jobs / 50.0, 1.0)
    competition_score = 1.0 - competition_ratio
    fit_score = stack_fit_ratio

    confidence = (
        0.4 * data_score
        + 0.3 * competition_score
        + 0.3 * fit_score
    )

    return round(confidence, 2)

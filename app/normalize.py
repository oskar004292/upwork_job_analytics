def normalize_pricing_type(v: str) -> str:
    return "hourly" if v.lower().startswith("hour") else "fixed"

def normalize_proposals_bucket(v: str) -> str:
    v = v.lower()
    if "<" in v or "less" in v:
        return "<5"
    if "50" in v:
        return "50+"
    return "20-50"

def normalize_budget(lo, hi):
    return lo, hi

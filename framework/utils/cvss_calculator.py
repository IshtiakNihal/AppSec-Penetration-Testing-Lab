def score(severity: str) -> float:
    mapping = {
        "critical": 9.8,
        "high": 8.2,
        "medium": 6.5,
        "low": 3.1,
        "info": 0.0,
    }
    return mapping.get(severity.lower(), 0.0)

from typing import Any

def calculate_risk_score(
    cvss_score: float | None,
    is_kev: bool,
    epss_score: float | None,
    is_direct_dependency: bool = True,
    project_criticality: str = "medium"
) -> tuple[int, dict[str, Any]]:
    """
    Calculate an explainable risk score from 0 to 100.
    """
    score = 0
    factors = {}

    # 1. Base CVSS Score (0-40 points)
    if cvss_score:
        cvss_points = int((cvss_score / 10.0) * 40)
        score += cvss_points
        factors["cvss_base"] = {"value": cvss_score, "points": cvss_points}

    # 2. CISA KEV (Known Exploited Vulnerability) (+30 points)
    if is_kev:
        score += 30
        factors["kev"] = {"value": True, "points": 30, "note": "Actively exploited in the wild"}

    # 3. EPSS Probability (0-15 points)
    if epss_score:
        epss_points = int(epss_score * 15)
        score += epss_points
        factors["epss"] = {"value": epss_score, "points": epss_points}

    # 4. Dependency Type (Direct vs Transitive) (0 or 10 points)
    if is_direct_dependency:
        score += 10
        factors["direct_dependency"] = {"value": True, "points": 10}

    # 5. Project Criticality Multiplier (Max +5 points)
    crit_bonus = {"low": 0, "medium": 2, "high": 5, "critical": 5}
    bonus = crit_bonus.get(project_criticality, 0)
    score += bonus
    factors["project_criticality"] = {"value": project_criticality, "points": bonus}

    # Cap at 100
    final_score = min(score, 100)

    return final_score, factors

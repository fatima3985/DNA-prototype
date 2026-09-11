
from behavior import compute_behavior_score

DEFAULT_WEIGHTS = {"writing": 0.45, "behavior": 0.55}


def compute_risk(writing_deviation: float, email_text: str,
                  weights: dict = None) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    behavior_result = compute_behavior_score(email_text)
    behavior_score = behavior_result["behavior_score"]

    risk_score = round(
        weights["writing"] * writing_deviation
        + weights["behavior"] * behavior_score, 1
    )

    return {
        "risk_score": risk_score,
        "risk_label": risk_label(risk_score),
        "writing_deviation": writing_deviation,
        "behavior_score": behavior_score,
        "category_scores": behavior_result["category_scores"],
        "reasons": explain(writing_deviation, behavior_result),
    }


def risk_label(score: float) -> str:
    if score < 30:
        return "LOW"
    elif score < 60:
        return "MEDIUM"
    elif score < 80:
        return "HIGH"
    else:
        return "CRITICAL"


def explain(writing_deviation: float, behavior_result: dict) -> list:
    reasons = []
    if writing_deviation >= 60:
        reasons.append("Writing style differs significantly from sender profile")
    cats = behavior_result["category_scores"]
    if cats["urgency"] >= 40:
        reasons.append("Unusual urgency detected")
    if cats["financial"] >= 40:
        reasons.append("Financial transfer request detected")
    if cats["secrecy"] >= 40:
        reasons.append("Confidentiality language detected")
    if cats["credential"] >= 40:
        reasons.append("Credential/login request detected")
    if cats["authority"] >= 40:
        reasons.append("Authority-figure pressure language detected")
    if not reasons:
        reasons.append("No significant red flags detected")
    return reasons



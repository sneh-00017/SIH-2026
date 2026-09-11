# Configurable default risk weights
DEFAULT_RISK_WEIGHTS = {
    "fall_detected": 50,
    "person_near_vehicle": 35,
    "restricted_zone": 30,
    "helmet_missing": 20,
    "safety_vest_missing": 15,
    "same_zone_presence": 15
}

PROTOTYPE_DISCLAIMER = (
    "HEURISTIC RISK PERCENTAGE: This percentage represents the share of the configured "
    "maximum hazard-weight score. It is not a calibrated probability of injury or fatality."
)


def calculate_risk_from_flags(data: dict, custom_weights: dict = None) -> dict:
    """
    Calculates safety risk score, risk level, hazards list, and human-readable explanations
    based on a dictionary of boolean safety flags and configurable risk weights.

    :param data: Dictionary containing boolean safety flags.
    :param custom_weights: Optional dictionary overriding default risk weights.
    :return: Dictionary containing risk_score, risk_level, hazards, explanation, and disclaimer.
    """
    weights = {**DEFAULT_RISK_WEIGHTS, **(custom_weights or {})}

    person_detected = data.get("person_detected", False)
    vehicle_detected = data.get("vehicle_detected", False)
    person_near_vehicle = data.get("person_near_vehicle", False)
    helmet_missing = data.get("helmet_missing", False)
    safety_vest_missing = data.get("safety_vest_missing", False)
    restricted_zone = data.get("restricted_zone", False)
    fall_detected = data.get("fall_detected", False)

    score = 0
    hazards = []
    explanation = []
    active_factors = []

    if fall_detected:
        score += weights.get("fall_detected", 50)
        hazards.append("Fall detected")
        explanation.append("A worker fall was detected.")
        active_factors.append(("Fall risk", weights.get("fall_detected", 50)))

    if person_near_vehicle:
        score += weights.get("person_near_vehicle", 35)
        hazards.append("Person near vehicle")
        explanation.append("A person was detected in dangerous proximity to a vehicle.")
        active_factors.append(("Vehicle proximity", weights.get("person_near_vehicle", 35)))
    elif person_detected and vehicle_detected:
        score += weights.get("same_zone_presence", 15)
        hazards.append("Person and vehicle in same zone")
        explanation.append("Both a person and a vehicle are present in the monitored zone.")
        active_factors.append(("Shared zone presence", weights.get("same_zone_presence", 15)))

    if restricted_zone:
        score += weights.get("restricted_zone", 30)
        hazards.append("Restricted zone breach")
        explanation.append("An unauthorized breach into a restricted safety zone was detected.")
        active_factors.append(("Restricted zone", weights.get("restricted_zone", 30)))

    if helmet_missing:
        score += weights.get("helmet_missing", 20)
        hazards.append("Helmet missing")
        explanation.append("At least one worker is missing a required safety helmet.")
        active_factors.append(("Helmet compliance", weights.get("helmet_missing", 20)))

    if safety_vest_missing:
        score += weights.get("safety_vest_missing", 15)
        hazards.append("Safety vest missing")
        explanation.append("At least one worker is missing a required high-visibility safety vest.")
        active_factors.append(("Visibility vest compliance", weights.get("safety_vest_missing", 15)))

    maximum_weight = sum(weights.values()) - weights.get("same_zone_presence", 0)
    score = round((score / maximum_weight) * 100) if maximum_weight else 0
    score = min(100, score)

    # Determine Risk Level based on score
    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Default explanation if no hazards were triggered
    if not explanation:
        explanation.append("No active safety hazards detected in the monitored area.")

    active_weight = sum(weight for _, weight in active_factors)
    risk_factors = [
        {"label": label, "percentage": round((weight / maximum_weight) * 100) if maximum_weight else 0, "weight": weight}
        for label, weight in active_factors
    ]

    return {
        "risk_score": score,
        "score": score,  # alias for backward compatibility
        "risk_level": risk_level,
        "hazards": hazards,
        "explanation": explanation,
        "risk_factors": risk_factors,
        "score_basis": {
            "active_weight": active_weight,
            "maximum_weight": maximum_weight,
            "meaning": "Percentage of configured maximum hazard weight",
        },
        "disclaimer": PROTOTYPE_DISCLAIMER,
        "weights_used": weights
    }


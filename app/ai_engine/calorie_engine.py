"""Calorie engine: BMI, BMR, TDEE, daily calorie target, ideal weight, and time-to-goal estimate."""

# Approximate kcal per kg body-weight change (mixed tissue/fat)
KCAL_PER_KG = 7700


def calculate_bmi(weight_kg, height_cm):
    """BMI = weight (kg) / height (m)^2."""
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 1)


def calculate_bmr(weight_kg, height_cm, age, gender):
    """Mifflin–St Jeor formula. gender is 'Male' or 'Female' (or similar)."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender and str(gender).strip().lower() in ("male", "m"):
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 0)


def calculate_tdee(bmr, activity_factor=1.4):
    """TDEE = BMR × activity factor. 1.2=sedentary, 1.55=moderate, 1.9=very active. Default 1.4 for students."""
    return round(bmr * activity_factor, 0)


def get_calorie_target(tdee, goal):
    """Return daily calorie target from goal. goal: Weight Loss / Maintain Weight / Muscle Gain."""
    goal = (goal or "").strip().lower()
    if "loss" in goal or "lose" in goal:
        return round(tdee - 500, 0)
    if "gain" in goal or "muscle" in goal:
        return round(tdee + 300, 0)
    return round(tdee, 0)  # maintain


def get_all_metrics(user, activity_factor=1.4, weight_kg_override=None):
    """Return dict with bmi, bmr, tdee, calorie_target for the given user object.
    If weight_kg_override is set (e.g. last logged weight), it is used instead of user.weight_kg."""
    weight = weight_kg_override if weight_kg_override is not None else (getattr(user, "weight_kg", 70) or 70)
    height = getattr(user, "height_cm", 170) or 170
    age = getattr(user, "age", 25) or 25
    gender = getattr(user, "gender", "Male") or "Male"
    goal = getattr(user, "goal", "Maintain Weight") or "Maintain Weight"

    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_factor)
    calorie_target = get_calorie_target(tdee, goal)

    return {
        "bmi": bmi,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,
        "activity_factor": activity_factor,
    }


def ideal_weight_kg(height_cm, target_bmi=22.0):
    """Return ideal weight (kg) for given height using target BMI. Default 22 = middle of healthy range 18.5–24.9."""
    height_m = height_cm / 100.0
    return round(target_bmi * (height_m ** 2), 1)


def healthy_bmi_range_kg(height_cm):
    """Return (min_kg, max_kg) for healthy BMI 18.5–24.9 for this height."""
    height_m = height_cm / 100.0
    min_kg = round(18.5 * (height_m ** 2), 1)
    max_kg = round(24.9 * (height_m ** 2), 1)
    return min_kg, max_kg


def estimate_weeks_to_weight(
    current_kg,
    target_kg,
    tdee,
    calorie_target,
    goal,
):
    """
    Estimate weeks to reach target weight given current calorie plan.
    Uses ~7700 kcal per kg change. Returns (weeks_float, message).
    """
    goal_lower = (goal or "").strip().lower()
    losing = "loss" in goal_lower or "lose" in goal_lower
    gaining = "gain" in goal_lower or "muscle" in goal_lower

    if losing:
        if current_kg <= target_kg:
            return None, "already_at_or_below"
        deficit_per_day = tdee - calorie_target
        if deficit_per_day <= 0:
            return None, "no_deficit"
        kg_per_week = (deficit_per_day * 7) / KCAL_PER_KG
        kg_per_week = min(kg_per_week, 1.0)  # cap ~1 kg/week for safety of estimate
        weeks = (current_kg - target_kg) / kg_per_week
        return weeks, "loss"
    elif gaining:
        if current_kg >= target_kg:
            return None, "already_at_or_above"
        surplus_per_day = calorie_target - tdee
        if surplus_per_day <= 0:
            return None, "no_surplus"
        kg_per_week = (surplus_per_day * 7) / KCAL_PER_KG
        kg_per_week = min(kg_per_week, 0.35)  # cap ~0.35 kg/week for muscle gain
        weeks = (target_kg - current_kg) / kg_per_week
        return weeks, "gain"
    else:
        return None, "maintain"
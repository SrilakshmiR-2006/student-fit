"""Calorie engine: BMI, BMR, TDEE, and daily calorie target."""


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


def get_all_metrics(user, activity_factor=1.4):
    """Return dict with bmi, bmr, tdee, calorie_target for the given user object."""
    weight = getattr(user, "weight_kg", 70) or 70
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
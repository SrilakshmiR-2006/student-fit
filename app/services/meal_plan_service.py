
"""Meal plan service: create and get meal plans."""
import json
from app.models.meal_plan import MealPlan


def create_meal_plan(session, user_id, calorie_target, plan_json, weekly_cost):
    """Save a new meal plan. plan_json can be a dict; it is stored as JSON string."""
    plan = MealPlan(
        user_id=user_id,
        calorie_target=float(calorie_target),
        plan_json=json.dumps(plan_json) if isinstance(plan_json, dict) else plan_json,
        weekly_cost=float(weekly_cost),
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def get_latest_meal_plan(session, user_id):
    """Return the most recent meal plan for this user, or None."""
    plan = (
        session.query(MealPlan)
        .filter(MealPlan.user_id == user_id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    return plan

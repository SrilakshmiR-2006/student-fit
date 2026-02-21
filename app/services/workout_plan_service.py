"""Workout plan service: create and get workout plans."""
import json
from app.models.workout_plan import WorkoutPlan


def create_workout_plan(session, user_id, plan_json):
    """Save a new workout plan. plan_json can be a dict; stored as JSON string."""
    plan = WorkoutPlan(
        user_id=user_id,
        plan_json=json.dumps(plan_json) if isinstance(plan_json, dict) else plan_json,
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def get_latest_workout_plan(session, user_id):
    """Return the most recent workout plan for this user, or None."""
    plan = (
        session.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.created_at.desc())
        .first()
    )
    return plan
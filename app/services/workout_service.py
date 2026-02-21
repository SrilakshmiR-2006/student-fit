"""Workout service: get all or filtered workouts."""
from app.models.workout import Workout


def get_all_workouts(session):
    """Return all workouts from the database."""
    return session.query(Workout).all()


def get_workouts_filtered(session, goal=None, equipment=None, difficulty=None):
    """Return workouts that match the given filters. None means no filter."""
    query = session.query(Workout)
    if goal:
        query = query.filter(Workout.goal == goal)
    if equipment is not None:
        query = query.filter(Workout.equipment_required == equipment)
    if difficulty:
        query = query.filter(Workout.difficulty == difficulty)
    return query.all()
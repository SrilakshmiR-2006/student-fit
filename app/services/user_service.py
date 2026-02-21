"""User service: get and create users."""
from app.models.users import User


def get_user_by_id(session, user_id):
    """Return the User with the given id, or None if not found."""
    return session.query(User).filter(User.id == user_id).first()


def create_user(
    session,
    name,
    age,
    gender,
    height_cm,
    weight_kg,
    goal,
    dietary_preference,
    budget,
    equipment,
    workout_minutes_per_day,
):
    """Create a new user, save to DB, and return it."""
    user = User(
        name=name,
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        goal=goal,
        dietary_preference=dietary_preference,
        budget=float(budget),
        equipment=equipment,
        workout_minutes_per_day=int(workout_minutes_per_day),
    )
    session.add(user)
    session.commit()
    session.refresh(user)  # so user.id is set
    return user
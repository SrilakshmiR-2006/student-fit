"""Recipe service: get all or filtered recipes."""
from app.models.recipes import Recipe


def get_all_recipes(session):
    """Return all recipes from the database."""
    return session.query(Recipe).all()


def get_recipes_filtered(
    session,
    diet_type=None,
    cuisine=None,
    max_cost_per_serving=None,
    meal_type=None,
):
    """Return recipes that match the given filters. None means no filter for that field."""
    query = session.query(Recipe)
    if diet_type:
        query = query.filter(Recipe.diet_type == diet_type)
    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)
    if max_cost_per_serving is not None:
        query = query.filter(Recipe.cost_per_serving <= max_cost_per_serving)
    if meal_type and hasattr(Recipe, "meal_type") and Recipe.meal_type is not None:
        query = query.filter(Recipe.meal_type == meal_type)
    return query.all()
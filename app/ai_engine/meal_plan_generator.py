# Meal plan JSON shape (use this in your prompt):
# { "days": [ { "day": 1, "date": "YYYY-MM-DD", "meals": [ { "meal_type": "Breakfast", "recipe_id": 1, "recipe_name": "...", "calories": 250 } ] } ], "total_weekly_cost": 500, "total_weekly_calories": 14000 }

import json
from app.ai_engine.gemini_client import generate_text
from app.services.user_service import get_user_by_id
from app.services.recipe_service import get_recipes_filtered, get_all_recipes
from app.services.meal_plan_service import create_meal_plan
from app.ai_engine.calorie_engine import get_all_metrics


def recipes_to_context(recipes):
    """Turn a list of Recipe objects into one string for the prompt."""
    lines = []
    for r in recipes:
        meal_type = getattr(r, "meal_type", None) or "Any"
        block = (
            f"ID: {r.id} | Name: {r.name} | Meal: {meal_type} | "
            f"Cal: {r.calories_per_serving} | P: {r.protein_g}g C: {r.carbs_g}g F: {r.fat_g}g | "
            f"Cost: {r.cost_per_serving} | Diet: {r.diet_type} | Cuisine: {r.cuisine or 'Any'}"
        )
        if getattr(r, "ingredients", None):
            block += f"\n  Ingredients: {r.ingredients[:200]}..."
        if getattr(r, "instructions", None):
            block += f"\n  Steps: {r.instructions[:200]}..."
        lines.append(block)
    return "\n\n".join(lines)


def build_meal_plan_prompt(user, recipes, calorie_target, budget, num_days=7):
    """Build the prompt for Gemini: user info + recipe list + JSON instructions."""
    recipe_context = recipes_to_context(recipes)
    goal = getattr(user, "goal", "Maintain Weight") or "Maintain Weight"
    diet = getattr(user, "dietary_preference", "Veg") or "Veg"
    cuisine_pref = getattr(user, "cuisine", None) or "any"
    budget = float(budget)

    prompt = f"""You are a student-friendly nutrition assistant. Create a {num_days}-day meal plan.

USER: Goal={goal}, Diet={diet}, Prefer cuisine={cuisine_pref}. Daily calorie target={calorie_target}, Weekly budget={budget}.

RULES:
- Use ONLY the recipes listed below. Pick by recipe ID.
- Total weekly cost must NOT exceed {budget}.
- Each day should have Breakfast, Lunch, Dinner (or similar). Match daily calories to about {calorie_target}.
- Output valid JSON only, no markdown. Shape:
{{"days": [{{"day": 1, "date": "YYYY-MM-DD", "meals": [{{"meal_type": "Breakfast", "recipe_id": 1, "recipe_name": "...", "calories": 250}}]}}], "total_weekly_cost": number, "total_weekly_calories": number}}

RECIPES (use only these):
{recipe_context}

Output the JSON meal plan now:"""

    return prompt


def generate_meal_plan(user, recipes, calorie_target, budget, num_days=7):
    """Call Gemini to generate a meal plan JSON; return dict or None on failure."""
    prompt = build_meal_plan_prompt(user, recipes, calorie_target, budget, num_days)
    raw = generate_text(prompt)
    if not raw:
        return None
    # Remove markdown code block if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        plan = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(plan, dict) or "days" not in plan:
        return None
    plan.setdefault("total_weekly_cost", 0)
    plan.setdefault("total_weekly_calories", 0)
    return plan


def generate_and_save_meal_plan(session, user_id):
    """Load user, get recipes, generate plan with Gemini, save and return plan dict."""
    user = get_user_by_id(session, user_id)
    if not user:
        return None
    metrics = get_all_metrics(user)
    calorie_target = metrics["calorie_target"]
    budget = float(getattr(user, "budget", 500) or 500)
    diet = (getattr(user, "dietary_preference", "Veg") or "Veg").strip().lower()
    # Max cost per serving so that 21 meals (7 days × 3) stay under budget
    max_cost_per_serving = budget / 21 if budget else None
    recipes = get_recipes_filtered(
        session, diet_type=diet, max_cost_per_serving=max_cost_per_serving
    )
    if not recipes:
        recipes = get_recipes_filtered(session, diet_type=diet)
    if not recipes:
        recipes = get_all_recipes(session)
    if not recipes:
        return None
    plan = generate_meal_plan(user, recipes, calorie_target, budget, 7)
    if not plan:
        return None
    weekly_cost = plan.get("total_weekly_cost", 0)
    create_meal_plan(session, user_id, calorie_target, plan, weekly_cost)
    return plan
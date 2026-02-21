"""Load data/recipes.csv into the recipes table. Run: uv run python -m scripts.load_recipes"""
import csv
from pathlib import Path

from app.database import SessionLocal
from app.models.recipes import Recipe

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes.csv"


def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Create data/recipes.csv first.")
        return

    db = SessionLocal()
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                calories_val = float(row.get("calories") or row.get("calories_per_serving") or 0)
                instructions_val = (row.get("preparation_steps") or row.get("instructions") or "").strip() or None
                recipe = Recipe(
                    name=row.get("name", "").strip(),
                    calories_per_serving=calories_val,
                    protein_g=float(row.get("protein_g", 0)),
                    carbs_g=float(row.get("carbs_g", 0)),
                    fat_g=float(row.get("fat_g", 0)),
                    diet_type=(row.get("diet_type") or "").strip().lower(),
                    cost_per_serving=float(row.get("cost_per_serving", 0)),
                    cuisine=(row.get("cuisine") or "").strip() or None,
                    ingredients=(row.get("ingredients") or "").strip() or None,
                    instructions=instructions_val,
                    meal_type=(row.get("meal_type") or "").strip() or None,
                )
                db.add(recipe)
                count += 1
            db.commit()
        print(f"Loaded {count} recipes into the database.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
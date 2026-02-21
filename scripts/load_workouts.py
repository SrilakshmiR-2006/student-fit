"""Load data/workouts.csv into the workouts table. Run: uv run python -m scripts.load_workouts"""
import csv
from pathlib import Path

from app.database import SessionLocal
from app.models.workout import Workout

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "workouts.csv"


def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Create data/workouts.csv first.")
        return

    db = SessionLocal()
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                w = Workout(
                    exercise_name=row.get("exercise_name", "").strip(),
                    category=row.get("category", "").strip(),
                    calories_burn_per_30min=float(row.get("calories_burn_per_30min", 0)),
                    difficulty=row.get("difficulty", "").strip(),
                    goal=row.get("goal", "").strip(),
                    equipment_required=row.get("equipment_required", "").strip(),
                    suggested_instructions=(row.get("suggested_instructions") or "").strip() or None,
                )
                db.add(w)
                count += 1
            db.commit()
        print(f"Loaded {count} workouts.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
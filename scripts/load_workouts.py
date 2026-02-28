import csv
from pathlib import Path

from app.database import SessionLocal
from app.models.workout import Workout

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "workouts.csv"


def load_workouts():
    """Load workouts into DB if not already loaded (prevents duplicates)."""

    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Create data/workouts.csv first.")
        return

    db = SessionLocal()
    try:
        existing = db.query(Workout).first()
        if existing:
            print("Workouts already loaded. Skipping.")
            return

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                try:
                    w = Workout(
                        exercise_name=row.get("exercise_name", "").strip(),
                        category=row.get("category", "").strip(),
                        calories_burn_per_30min=float(
                            row.get("calories_burn_per_30min", 0) or 0
                        ),
                        difficulty=row.get("difficulty", "").strip(),
                        goal=row.get("goal", "").strip(),
                        equipment_required=row.get("equipment_required", "").strip(),
                        suggested_instructions=(
                            row.get("suggested_instructions") or ""
                        ).strip() or None,
                    )
                    db.add(w)
                    count += 1
                except Exception as e:
                    print(f"Skipping row due to error: {e}")

            db.commit()

        print(f"Loaded {count} workouts into database.")

    finally:
        db.close()

if __name__ == "__main__":
    load_workouts()
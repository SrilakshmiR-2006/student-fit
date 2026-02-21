
"""One-time migration: add ingredients and instructions columns to recipes table.
Run if you already have a recipes table from before these columns existed: uv run python -m scripts.migrate_recipes_add_ingredients_instructions"""
from sqlalchemy import text

from app.database import engine


def main():
    with engine.connect() as conn:
        for col in ("ingredients", "instructions"):
            try:
                conn.execute(text(f"ALTER TABLE recipes ADD COLUMN IF NOT EXISTS {col} TEXT"))
                conn.commit()
                print(f"Added column: {col}")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"Column {col} already exists, skipping.")
                else:
                    raise
    print("Migration done.")


if __name__ == "__main__":
    main()

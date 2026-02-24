"""One-time migration: add cuisine column to users table.
Run if you already have a users table: uv run python -m scripts.migrate_users_add_cuisine"""
from sqlalchemy import text

from app.database import engine


def main():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cuisine VARCHAR(100)"))
            conn.commit()
            print("Added column: cuisine")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("Column cuisine already exists, skipping.")
            else:
                raise
    print("Migration done.")


if __name__ == "__main__":
    main()
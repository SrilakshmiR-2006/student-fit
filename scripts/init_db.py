"""Create all database tables. Run from project root: uv run python -m scripts.init_db"""
from urllib.parse import urlparse

from app.config import DATABASE_URL
from app.database import engine, Base
from app.models import users, meal_plan, workout_plan, progress_log, recipes, workout

# Show which database we're using (so you can find it in pgAdmin)
db_name = (urlparse(DATABASE_URL).path or "/").lstrip("/") or "postgres"
print(f"Using database: {db_name!r}")

Base.metadata.create_all(bind=engine)
print("Tables created.")
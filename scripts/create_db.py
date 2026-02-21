"""Create the database if it doesn't exist. Run first: uv run python -m scripts.create_db"""
import os
import sys
from pathlib import Path

# Load .env from project root
root = Path(__file__).resolve().parent.parent
dotenv_path = root / ".env"
if dotenv_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)
else:
    print("No .env file found. Set DATABASE_URL in the environment or create .env in the project root.")
    sys.exit(1)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or not DATABASE_URL.strip().startswith("postgresql"):
    print("DATABASE_URL is missing or not a PostgreSQL URL in .env")
    sys.exit(1)

from urllib.parse import urlparse, urlunparse

def main():
    parsed = urlparse(DATABASE_URL)
    db_name = (parsed.path or "/").lstrip("/") or "postgres"
    if db_name == "postgres":
        print("Already using default database 'postgres'. Nothing to create.")
        return

    # Connect to default 'postgres' database to run CREATE DATABASE
    parts = list(parsed)
    parts[2] = "/postgres"
    postgres_url = urlunparse(parts)

    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("psycopg2 is required. Run: uv add psycopg2-binary")
        sys.exit(1)

    conn = psycopg2.connect(postgres_url)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # PostgreSQL doesn't have CREATE DATABASE IF NOT EXISTS; catch duplicate
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name!r} created.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database {db_name!r} already exists.")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
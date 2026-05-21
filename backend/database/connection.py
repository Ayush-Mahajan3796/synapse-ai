import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Get database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite during development if no URL is provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./synapse.db"

# Check if using PostgreSQL/pgvector
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# For SQLite, we need to allow multithreaded access
connect_args = {"check_same_thread": False} if not IS_POSTGRES else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection helper for FastAPI routes to get database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_schema():
    """Apply simple SQLite schema migrations for local development."""
    if IS_POSTGRES:
        return

    with engine.begin() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        if result.fetchone() is None:
            return

        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if 'password_hash' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
        if 'salt' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN salt VARCHAR(100)"))

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Get database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite during development if no URL is provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./synapse.db"

# Detect database dialect
IS_POSTGRES = DATABASE_URL.startswith("postgresql")
IS_MYSQL    = DATABASE_URL.startswith("mysql")
IS_SQLITE   = DATABASE_URL.startswith("sqlite")


def _ensure_mysql_db_exists(url: str):
    """
    If connecting to MySQL, try to auto-create the database if it doesn't exist.
    This is a best-effort helper and is skipped if the server is unreachable.
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        db_name = parsed.path.lstrip("/")
        # Build a URL that connects to the server without specifying a database
        server_url = url.replace(f"/{db_name}", "/")
        tmp_engine = create_engine(server_url, connect_args={})
        with tmp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        tmp_engine.dispose()
        logging.info("MySQL database '%s' ensured.", db_name)
    except Exception as err:
        logging.warning("Could not auto-create MySQL database: %s", err)


if IS_MYSQL:
    _ensure_mysql_db_exists(DATABASE_URL)

# For SQLite, we need to allow multithreaded access
connect_args = {"check_same_thread": False} if IS_SQLITE else {}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    # Test connection immediately
    with engine.connect() as conn:
        pass
except Exception as e:
    logging.error(f"MySQL connection failed: {e}")
    logging.info("Falling back to local SQLite database (synapse.db)...")
    DATABASE_URL = "sqlite:///./synapse.db"
    IS_SQLITE = True
    IS_MYSQL = False
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)

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
    if not IS_SQLITE:
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

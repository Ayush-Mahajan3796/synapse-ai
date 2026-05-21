import os
import logging
from urllib.parse import quote_plus, urlparse, urlunparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Get database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB = os.getenv("MONGODB_DB", "synapse")

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

USE_MONGODB = False
mongo_client = None
mongo_db = None
mongo_users_collection = None


def normalize_mongodb_url(url: str) -> str:
    try:
        parsed = urlparse(url)
    except Exception:
        return url

    if parsed.scheme not in ("mongodb", "mongodb+srv"):
        return url

    if parsed.username is None and parsed.password is None:
        return url

    username = quote_plus(parsed.username) if parsed.username else None
    password = quote_plus(parsed.password) if parsed.password else None

    auth = ""
    if username:
        auth = username
        if password:
            auth += f":{password}"
        auth += "@"

    netloc = auth + (parsed.hostname or "")
    if parsed.port:
        netloc += f":{parsed.port}"

    normalized = parsed._replace(netloc=netloc)
    return urlunparse(normalized)


if MONGODB_URL:
    if "<" in MONGODB_URL or ">" in MONGODB_URL:
        logging.warning("MONGODB_URL appears to contain placeholder values; MongoDB login will be disabled until a valid URL is provided.")
    else:
        try:
            safe_url = normalize_mongodb_url(MONGODB_URL)
            if safe_url != MONGODB_URL:
                logging.info("Normalized MongoDB URL credentials for safe parsing.")
            mongo_client = MongoClient(safe_url, serverSelectionTimeoutMS=5000)
            mongo_db = mongo_client[MONGODB_DB]
            mongo_users_collection = mongo_db["users"]
            mongo_users_collection.create_index("username", unique=True)
            mongo_users_collection.create_index("email", unique=True, sparse=True)
            USE_MONGODB = True
        except PyMongoError as err:
            logging.warning("Unable to initialize MongoDB for login: %s", err)
            mongo_client = None
            mongo_db = None
            mongo_users_collection = None


def get_db():
    """Dependency injection helper for FastAPI routes to get database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_users_collection():
    """Return the MongoDB users collection when MongoDB auth is enabled."""
    return mongo_users_collection


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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

# Initialize Database tables
from database.connection import Base, engine, ensure_sqlite_schema
import database.models
Base.metadata.create_all(bind=engine)
ensure_sqlite_schema()

from routes import upload, chat, auth

app = FastAPI(title="SynapseAI API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For MVP, open to all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Research Copilot API"}

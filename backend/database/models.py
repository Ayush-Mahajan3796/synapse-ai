from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, PickleType
from sqlalchemy.sql import func
from database.connection import Base, IS_POSTGRES

# Dynamically set embedding column type based on database dialect
if IS_POSTGRES:
    try:
        from pgvector.sqlalchemy import Vector
        EmbeddingType = Vector(384)  # For all-MiniLM-L6-v2 embeddings (384 dimensions)
    except ImportError:
        EmbeddingType = PickleType
else:
    # Fallback for local SQLite development
    EmbeddingType = PickleType

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String(500), nullable=True)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(EmbeddingType, nullable=True)
    page_number = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # Stored as serialized JSON string

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), index=True, default="default")
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    planner_output = Column(Text, nullable=True)
    selected_agents = Column(String(255), nullable=True)
    execution_time = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String(255), nullable=False)
    completion_percentage = Column(Float, default=0.0)
    weak_areas = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

from sqlalchemy.orm import Session
from database.models import Chat, Document, DocumentChunk, AgentLog, LearningProgress, User
from typing import List, Optional
import json

# --- Chat Operations ---

def get_chat_history(db: Session, session_id: str, user_id: Optional[int] = None, limit: int = 50) -> List[Chat]:
    """Retrieve chat history sorted chronologically for a specific session ID and user ID."""
    query = db.query(Chat).filter(Chat.session_id == session_id)
    if user_id is not None:
        query = query.filter(Chat.user_id == user_id)
    return query.order_by(Chat.id.asc()).limit(limit).all()


def create_chat_message(db: Session, session_id: str, message: str, response: str, user_id: Optional[int] = None) -> Chat:
    """Save a user message and LLM/agent response to the chats table."""
    db_chat = Chat(
        user_id=user_id,
        session_id=session_id,
        message=message,
        response=response
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

# --- Document Operations ---

def create_user(
    db: Session,
    username: str,
    password_hash: str,
    salt: str,
    email: Optional[str] = None
):
    """Create a new user account record."""
    db_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        salt=salt
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_document(db: Session, filename: str, file_path: Optional[str] = None, user_id: Optional[int] = None) -> Document:
    """Create a new document log entry."""
    db_doc = Document(
        filename=filename,
        file_path=file_path,
        user_id=user_id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def create_document_chunk(
    db: Session, 
    document_id: int, 
    chunk_text: str, 
    embedding: List[float], 
    page_number: Optional[int] = None, 
    metadata: Optional[dict] = None
) -> DocumentChunk:
    """Save a chunk of extracted document text along with its generated vector embedding."""
    metadata_str = json.dumps(metadata) if metadata else None
    db_chunk = DocumentChunk(
        document_id=document_id,
        chunk_text=chunk_text,
        embedding=embedding,
        page_number=page_number,
        metadata_json=metadata_str
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

# --- Agent Log Operations ---

def create_agent_log(
    db: Session, 
    planner_output: str, 
    selected_agents: str, 
    execution_time: float, 
    confidence_score: float, 
    user_id: Optional[int] = None
) -> AgentLog:
    """Log Planner Agent decisions and metrics for evaluation dashboards."""
    db_log = AgentLog(
        user_id=user_id,
        planner_output=planner_output,
        selected_agents=selected_agents,
        execution_time=execution_time,
        confidence_score=confidence_score
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# --- Learning Progress Operations ---

def create_or_update_learning_progress(
    db: Session, 
    topic: str, 
    completion_percentage: float, 
    weak_areas: Optional[str] = None, 
    user_id: Optional[int] = None
) -> LearningProgress:
    """Log or update learning metrics for adaptive dashboard views."""
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == user_id, 
        LearningProgress.topic == topic
    ).first()
    
    if progress:
        progress.completion_percentage = completion_percentage
        if weak_areas:
            progress.weak_areas = weak_areas
    else:
        progress = LearningProgress(
            user_id=user_id,
            topic=topic,
            completion_percentage=completion_percentage,
            weak_areas=weak_areas
        )
        db.add(progress)
        
    db.commit()
    db.refresh(progress)
    return progress

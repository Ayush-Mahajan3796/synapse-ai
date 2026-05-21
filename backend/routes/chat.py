from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database import crud
from models.schemas import ChatRequest, ChatResponse, ChatHistoryItem
from rag.retriever import rag_store
from groq import Groq
import os

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    x_user_id: Optional[int] = Header(None), 
    db: Session = Depends(get_db)
):
    # Retrieve relevant contexts using hybrid search, filtered by current user
    contexts = rag_store.retrieve(db, request.query, user_id=x_user_id, top_k=3)

    # Include only the last 3 chat history items to avoid token limit issues
    history_items = crud.get_chat_history(db, session_id=request.session_id, user_id=x_user_id, limit=3)
    history_context = "\n".join(
        [f"User: {item.message}\nAssistant: {item.response}" for item in history_items[-3:]]
    ) if history_items else ""
    
    # Truncate contexts to avoid exceeding token limits
    truncated_contexts = [c[:500] if len(c) > 500 else c for c in contexts]
    context_str = "\n".join([f"[{i+1}] {c}" for i, c in enumerate(truncated_contexts)])
    
    system_prompt = (
        "You are SynapseAI, an intelligent research and learning copilot.\n"
        "Use the following context to answer the user's question.\n"
        "If the answer comes from the user's documents, explicitly say so.\n"
        "If the context doesn't contain the answer, state that clearly.\n\n"
    )
    if history_context:
        system_prompt += f"Recent Conversation:\n{history_context}\n\n"
    system_prompt += f"Documents:\n{context_str}"
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return ChatResponse(answer="Error: GROQ_API_KEY is not set in backend.", sources=[])

    client = Groq(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            max_tokens=512
        )
        answer = response.choices[0].message.content
        
        # Save query and response to the database with the user association
        crud.create_chat_message(
            db, 
            session_id=request.session_id, 
            message=request.query, 
            response=answer,
            user_id=x_user_id
        )
        
        return ChatResponse(answer=answer, sources=contexts)
    except Exception as e:
        error_answer = f"Error calling Groq: {str(e)}"
        # Save error message to ensure consistency in logs
        crud.create_chat_message(
            db, 
            session_id=request.session_id, 
            message=request.query, 
            response=error_answer,
            user_id=x_user_id
        )
        return ChatResponse(answer=error_answer, sources=[])

@router.get("/chat/history", response_model=List[ChatHistoryItem])
def get_history(
    session_id: str = "default", 
    x_user_id: Optional[int] = Header(None), 
    db: Session = Depends(get_db)
):
    """Fetch stored chat history for a session and specific user."""
    chats = crud.get_chat_history(db, session_id=session_id, user_id=x_user_id)
    return chats

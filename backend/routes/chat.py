from fastapi import APIRouter, Depends, Header, HTTPException
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
    try:
        contexts = rag_store.retrieve(db, request.query, user_id=x_user_id, top_k=3)
    except Exception:
        contexts = []

    # Include only the last 3 chat history items to avoid token limit issues
    try:
        history_items = crud.get_chat_history(db, session_id=request.session_id, user_id=x_user_id, limit=3)
    except Exception:
        history_items = []

    history_context = "\n".join(
        [f"User: {item.message}\nAssistant: {item.response}" for item in history_items[-3:]]
    ) if history_items else ""
    
    # Truncate contexts to avoid exceeding token limits
    truncated_contexts = [c[:500] if len(c) > 500 else c for c in contexts]
    context_str = "\n".join([f"[{i+1}] {c}" for i, c in enumerate(truncated_contexts)])
    
    system_prompt = (
        "You are SynapseAI, an intelligent research and learning copilot.\n"
        "Use the following context extracted from the user's uploaded documents to answer their question.\n"
        "If the answer is found in the documents, cite it clearly.\n"
        "If the context is empty or doesn't contain the answer, say so honestly.\n\n"
    )
    if history_context:
        system_prompt += f"Recent Conversation:\n{history_context}\n\n"
    if context_str:
        system_prompt += f"Document Context:\n{context_str}"
    else:
        system_prompt += "Document Context: No relevant document content found. Answer from general knowledge if possible."
    
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
        try:
            crud.create_chat_message(
                db, 
                session_id=request.session_id, 
                message=request.query, 
                response=answer,
                user_id=x_user_id
            )
        except Exception:
            pass  # Don't fail the response if history saving fails
        
        return ChatResponse(answer=answer, sources=contexts)
    except Exception as e:
        return ChatResponse(answer=f"Error calling Groq AI: {str(e)}", sources=[])


@router.get("/chat/history", response_model=List[ChatHistoryItem])
def get_history(
    session_id: str = "default", 
    x_user_id: Optional[int] = Header(None), 
    db: Session = Depends(get_db)
):
    """Fetch stored chat history for a session and specific user."""
    try:
        chats = crud.get_chat_history(db, session_id=session_id, user_id=x_user_id)
        return chats
    except Exception:
        return []


@router.delete("/chat/clear")
def clear_chat_history(
    x_user_id: Optional[int] = Header(None), 
    db: Session = Depends(get_db)
):
    """Delete all chat history for the current user."""
    if x_user_id is None:
        raise HTTPException(status_code=400, detail="X-User-Id header is missing")
    try:
        crud.delete_user_chats(db, user_id=x_user_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")

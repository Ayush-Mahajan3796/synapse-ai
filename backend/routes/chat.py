from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from rag.retriever import rag_store
from groq import Groq
import os

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Retrieve relevant contexts
    contexts = rag_store.retrieve(request.query, top_k=4)
    
    # Construct prompt
    context_str = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)])
    system_prompt = (
        "You are an AI Research & Learning Copilot. Use the following context to answer the user's question.\n"
        "If the context doesn't contain the answer, say so.\n\n"
        f"Context:\n{context_str}"
    )
    
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
            max_tokens=1024
        )
        answer = response.choices[0].message.content
        return ChatResponse(answer=answer, sources=contexts)
    except Exception as e:
        return ChatResponse(answer=f"Error calling Groq: {str(e)}", sources=[])

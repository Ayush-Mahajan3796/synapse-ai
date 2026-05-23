from fastapi import APIRouter, UploadFile, File, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from database import crud
from database.models import Document
from models.schemas import DocumentResponse
from rag.retriever import rag_store
from utils.pdf_utils import extract_text_from_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), 
    x_user_id: Optional[int] = Header(None), 
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        text, ocr_used = extract_text_from_pdf(content)
        
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from the uploaded PDF.")

        # 1. Create a Document record, linking it to the current user_id
        db_doc = crud.create_document(db, filename=file.filename, user_id=x_user_id)
        
        # 2. Ingest the text and save embeddings
        chunks_added = rag_store.ingest_text(db=db, document_id=db_doc.id, text=text)
        
        return {
            "message": f"Successfully processed {file.filename}", 
            "document_id": db_doc.id,
            "chunks_added": chunks_added,
            "ocr_used": ocr_used
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents", response_model=List[DocumentResponse])
def get_user_documents(x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    """Retrieve all document upload records for the current user."""
    if x_user_id is None:
        return []
    try:
        return db.query(Document).filter(Document.user_id == x_user_id).order_by(Document.id.desc()).all()
    except Exception:
        return []

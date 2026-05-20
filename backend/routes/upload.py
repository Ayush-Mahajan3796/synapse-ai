from fastapi import APIRouter, UploadFile, File
from models.schemas import ChatResponse
from rag.retriever import rag_store
from utils.pdf_utils import extract_text_from_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)
        chunks_added = rag_store.ingest_text(text)
        return {"message": f"Successfully processed {file.filename}", "chunks_added": chunks_added}
    except Exception as e:
        return {"error": str(e)}

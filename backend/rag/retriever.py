import re
import json
import numpy as np
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi

from database.connection import SessionLocal, IS_POSTGRES
from database.models import DocumentChunk, Document
from utils.embeddings import get_embedding

class HybridRetriever:
    """Enterprise-grade Hybrid Search combining BM25 keyword search and Dense Vector similarity.
    
    Ensures complete multi-tenant user isolation.
    """
    
    def __init__(self):
        pass

    def _tokenize(self, text: str):
        return re.findall(r'\w+', text.lower())

    def ingest_text(self, db: Session, document_id: int, text: str, chunk_size=800, overlap=150) -> int:
        """Split text into chunks, generate embeddings, and save them in the database."""
        words = text.split()
        chunks = []
        i = 0
        words_per_chunk = chunk_size // 5  # approx 5 chars per word
        words_overlap = overlap // 5
        
        while i < len(words):
            chunk = " ".join(words[i:i + words_per_chunk])
            chunks.append(chunk)
            i += (words_per_chunk - words_overlap)

        # Store chunks in database
        for idx, chunk_text in enumerate(chunks):
            embedding = get_embedding(chunk_text)
            
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_text=chunk_text,
                embedding=embedding,
                page_number=idx + 1
            )
            db.add(db_chunk)
            
        db.commit()
        return len(chunks)

    def _vector_search(self, db: Session, query_embedding: list, user_id: int, top_k: int) -> list:
        """Perform semantic vector search filtered by user_id."""
        if IS_POSTGRES:
            # Query using pgvector cosine distance operator, filtered by owner
            results = (
                db.query(DocumentChunk.id, DocumentChunk.chunk_text, Document.filename)
                .join(Document, Document.id == DocumentChunk.document_id)
                .filter(Document.user_id == user_id)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
                .all()
            )
            return [(chunk_id, chunk_text, filename) for chunk_id, chunk_text, filename in results]
        else:
            # Fallback for SQLite: fetch chunks owned by the user and calculate similarity
            rows = (
                db.query(DocumentChunk.id, DocumentChunk.chunk_text, DocumentChunk.embedding, Document.filename)
                .join(Document, Document.id == DocumentChunk.document_id)
                .filter(Document.user_id == user_id)
                .all()
            )
            if not rows:
                return []
            
            similarities = []
            for chunk_id, chunk_text, embedding, filename in rows:
                if embedding is None:
                    continue
                emb_a = np.array(query_embedding)
                emb_b = np.array(embedding)
                sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b) + 1e-8)
                similarities.append((sim, chunk_id, chunk_text, filename))
            
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [(chunk_id, text, filename) for _, chunk_id, text, filename in similarities[:top_k]]

    def retrieve(self, db: Session, query: str, user_id, top_k: int = 4) -> list:
        """Perform Hybrid Search using Reciprocal Rank Fusion (RRF), fully isolated by user_id."""
        if user_id is None:  # explicit None check — user_id=0 or 1 are valid
            return []
            
        # 1. Generate query embedding
        query_embedding = get_embedding(query)
        
        # 2. Get Vector search results (isolated to user_id)
        vector_results = self._vector_search(db, query_embedding, user_id=user_id, top_k=20)
        
        # 3. Get BM25 lexical results (isolated to user_id)
        bm25_results = []
        user_chunks = (
            db.query(DocumentChunk.id, DocumentChunk.chunk_text, Document.filename)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(Document.user_id == user_id)
            .all()
        )
        
        if user_chunks:
            corpus = [self._tokenize(chunk_text) for _, chunk_text, _ in user_chunks]
            bm25 = BM25Okapi(corpus)
            tokenized_query = self._tokenize(query)
            scores = bm25.get_scores(tokenized_query)
            top_indices = np.argsort(scores)[::-1][:20]
            
            for idx in top_indices:
                if scores[idx] > 0:
                    chunk_id, chunk_text, filename = user_chunks[idx]
                    bm25_results.append((chunk_id, chunk_text, filename))

        # 4. Apply Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k_const = 60
        
        for rank, (chunk_id, _, _) in enumerate(vector_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k_const + rank + 1))
            
        for rank, (chunk_id, _, _) in enumerate(bm25_results):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k_const + rank + 1))

        if not rrf_scores:
            return []

        sorted_chunks = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        final_results = []
        db_chunks = (
            db.query(DocumentChunk.id, DocumentChunk.chunk_text, Document.filename)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(DocumentChunk.id.in_(sorted_chunks[:top_k]))
            .all()
        )
        chunk_lookup = {chunk_id: (chunk_text, filename) for chunk_id, chunk_text, filename in db_chunks}
        for chunk_id in sorted_chunks[:top_k]:
            if chunk_id in chunk_lookup:
                chunk_text, filename = chunk_lookup[chunk_id]
                final_results.append(f"Source: {filename} — {chunk_text}")
                
        return final_results

# Singleton instance
rag_store = HybridRetriever()

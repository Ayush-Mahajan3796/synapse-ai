import re
from collections import Counter
import math

class SimpleRAG:
    """Simple Keyword Search RAG (Pure Python) to bypass ML hanging issues on Windows."""

    def __init__(self):
        self.texts = []
        
    def _chunk_text(self, text: str, chunk_size=800, overlap=150):
        words = text.split()
        chunks = []
        i = 0
        words_per_chunk = chunk_size // 5 # approx 5 chars per word
        words_overlap = overlap // 5
        
        while i < len(words):
            chunk = " ".join(words[i:i + words_per_chunk])
            chunks.append(chunk)
            i += (words_per_chunk - words_overlap)
        return chunks

    def ingest_text(self, text: str):
        chunks = self._chunk_text(text)
        self.texts.extend(chunks)
        return len(chunks)
    
    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())
        
    def retrieve(self, query: str, top_k: int = 4):
        if not self.texts:
            return []
            
        q_tokens = set(self._tokenize(query))
        
        scores = []
        for idx, text in enumerate(self.texts):
            text_tokens = self._tokenize(text)
            text_counter = Counter(text_tokens)
            score = sum(text_counter[q] for q in q_tokens)
            scores.append((score, text))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        return [text for score, text in scores[:top_k]]

# Singleton instance
rag_store = SimpleRAG()

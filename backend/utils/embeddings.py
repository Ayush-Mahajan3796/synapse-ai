from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

_model = None

def get_embedding_model():
    """Lazily load the SentenceTransformer model to avoid server startup delays."""
    global _model
    if _model is None:
        # Load the 384-dimension all-MiniLM-L6-v2 model
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(text: str) -> List[float]:
    """Generate a 384-dimensional vector embedding for the input text."""
    model = get_embedding_model()
    embedding = model.encode(text)
    # Convert numpy array to list of floats
    return embedding.tolist()

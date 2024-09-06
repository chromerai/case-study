
from sentence_transformers import SentenceTransformer
from typing import List

def embed_text(text: str) -> List[float]:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    response = embedder.encode([text])
    return response.data[0].embedding
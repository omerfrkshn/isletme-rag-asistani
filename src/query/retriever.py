from src.embed.db import search
from src.embed.embedder import embed_query

# multilingual-e5 kosinüs skorları için kaba eşik: bunun altı "muhtemelen kapsam dışı"
RELEVANCE_THRESHOLD = 0.78


def retrieve(dataset: str, question: str, top_k: int = 5) -> list[dict]:
    query_embedding = embed_query(question)
    return search(dataset, query_embedding, top_k=top_k)


def has_relevant_context(results: list[dict]) -> bool:
    return bool(results) and results[0]["score"] >= RELEVANCE_THRESHOLD

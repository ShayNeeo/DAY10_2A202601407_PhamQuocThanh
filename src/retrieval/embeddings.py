from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = _load_model(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


def build_embeddings(model_name: str, google_api_key: str | None = None) -> Embeddings:
    if "gecko" in model_name or "text-embedding" in model_name or "gemini" in model_name:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=google_api_key)
    return MiniLMEmbeddings(model_name)


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


class GeminiEmbeddings(Embeddings):
    def __init__(self, model: str, api_key: str | None = None):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        self._backend = GoogleGenerativeAIEmbeddings(model=model, google_api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._backend.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._backend.embed_query(text)


def build_embeddings(embedding_model: str, google_api_key: str | None = None) -> Embeddings:
    if "gemini" in embedding_model.lower():
        return GeminiEmbeddings(model=embedding_model, api_key=google_api_key)
    return MiniLMEmbeddings(embedding_model)

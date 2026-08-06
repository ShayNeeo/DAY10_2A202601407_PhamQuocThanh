from dataclasses import replace
from pathlib import Path
import tempfile
import pandas as pd
import pytest

from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex


def test_embedding_index_build_and_search():
    settings = load_settings()
    df = pd.DataFrame(
        [
            {
                "paper_id": "p001",
                "title": "Agentic AI RAG Architectures",
                "summary": "This paper investigates agentic RAG and vector database observability.",
                "authors_joined": "Alice, Bob",
                "categories_joined": "Computer Science",
                "published": "2026-01-01",
                "abs_url": "http://example.com/p001",
                "pdf_url": "http://example.com/p001.pdf",
                "text_for_embedding": "Title: Agentic AI RAG Architectures\nSummary: This paper investigates agentic RAG and vector database observability.",
            }
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        new_paths = replace(settings.paths, chroma_dir=tmp_path / "chroma")
        settings = replace(settings, paths=new_paths)
        manifest_path = tmp_path / "embeddings.json"

        index = LocalEmbeddingIndex.build(df, settings, embeddings_output_path=manifest_path)
        assert manifest_path.exists()
        assert index.collection.count() == 1

        # Test lookup
        record = index.lookup("p001")
        assert record is not None
        assert record["title"] == "Agentic AI RAG Architectures"

        # Test semantic search
        results = index.search("agentic RAG", top_k=1)
        assert len(results) == 1
        assert results[0].paper_id == "p001"

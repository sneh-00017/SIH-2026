"""Local SBERT embedding service for SafeSight text analysis."""

from pathlib import Path
from threading import Lock

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_DIRECTORY = Path(__file__).resolve().parent / "models" / "all-MiniLM-L6-v2"

_model = None
_model_lock = Lock()


def get_model() -> SentenceTransformer:
    """Load SBERT once and keep its files inside this backend project."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                MODEL_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
                _model = SentenceTransformer(
                    str(MODEL_DIRECTORY) if MODEL_DIRECTORY.exists() else MODEL_NAME,
                    cache_folder=str(MODEL_DIRECTORY.parent),
                )
                if not MODEL_DIRECTORY.exists():
                    _model.save_pretrained(str(MODEL_DIRECTORY))
    return _model


def embed_sentences(sentences: list[str]) -> list[list[float]]:
    embeddings = get_model().encode(sentences, normalize_embeddings=True)
    return embeddings.tolist()


def cosine_similarity(left: str, right: str) -> float:
    embeddings = get_model().encode([left, right], normalize_embeddings=True)
    return float(embeddings[0] @ embeddings[1])

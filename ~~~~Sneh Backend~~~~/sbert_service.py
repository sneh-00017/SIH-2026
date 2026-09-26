
"""Local SBERT embedding service for SafeSight text analysis."""

from pathlib import Path
from threading import Lock

import torch
from transformers import AutoModel, AutoTokenizer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_DIRECTORY = Path(__file__).resolve().parent / "models" / "all-MiniLM-L6-v2"

_model = None
_tokenizer = None
_model_lock = Lock()


def get_model_and_tokenizer():
    """Load the model and tokenizer once."""
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        with _model_lock:
            if _model is None or _tokenizer is None:
                MODEL_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
                source = str(MODEL_DIRECTORY) if MODEL_DIRECTORY.exists() else MODEL_NAME

                _tokenizer = AutoTokenizer.from_pretrained(
                    source, cache_dir=str(MODEL_DIRECTORY.parent)
                )
                _model = AutoModel.from_pretrained(
                    source, cache_dir=str(MODEL_DIRECTORY.parent)
                )
                _model.eval()

                if not MODEL_DIRECTORY.exists():
                    _tokenizer.save_pretrained(str(MODEL_DIRECTORY))
                    _model.save_pretrained(str(MODEL_DIRECTORY))

    return _model, _tokenizer


def embed_sentences(sentences: list[str]) -> list[list[float]]:
    """Create normalized 384-dimensional sentence embeddings."""
    model, tokenizer = get_model_and_tokenizer()

    encoded = tokenizer(
        sentences,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    with torch.inference_mode():
        token_vectors = model(**encoded).last_hidden_state

    mask = encoded["attention_mask"].unsqueeze(-1).expand(token_vectors.size()).float()
    embeddings = (token_vectors * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

    return embeddings.cpu().tolist()


def cosine_similarity(left: str, right: str) -> float:
    """Calculate cosine similarity between two sentences."""
    embeddings = torch.tensor(embed_sentences([left, right]))
    return float(torch.dot(embeddings[0], embeddings[1]))
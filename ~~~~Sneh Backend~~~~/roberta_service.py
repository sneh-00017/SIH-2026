"""Local RoBERTa embedding service for SafeSight text analysis."""

from pathlib import Path
from threading import Lock

MODEL_NAME = "roberta-base"
MODEL_DIRECTORY = Path(__file__).resolve().parent / "models" / "roberta-base"

_model = None
_tokenizer = None
_model_lock = Lock()


def get_model_and_tokenizer():
    """Load RoBERTa once and persist downloaded files inside this project."""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        with _model_lock:
            if _model is None or _tokenizer is None:
                from transformers import AutoModel, AutoTokenizer

                MODEL_DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
                source = str(MODEL_DIRECTORY) if MODEL_DIRECTORY.exists() else MODEL_NAME
                _tokenizer = AutoTokenizer.from_pretrained(source, cache_dir=str(MODEL_DIRECTORY.parent))
                _model = AutoModel.from_pretrained(source, cache_dir=str(MODEL_DIRECTORY.parent))
                _model.eval()
                if not MODEL_DIRECTORY.exists():
                    _tokenizer.save_pretrained(str(MODEL_DIRECTORY))
                    _model.save_pretrained(str(MODEL_DIRECTORY))
    return _model, _tokenizer


def embed_sentences(sentences: list[str]) -> list[list[float]]:
    """Mean-pool token vectors into normalized 768-dimensional text embeddings."""
    import torch

    model, tokenizer = get_model_and_tokenizer()
    encoded = tokenizer(sentences, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.inference_mode():
        token_vectors = model(**encoded).last_hidden_state
    mask = encoded["attention_mask"].unsqueeze(-1).expand(token_vectors.size()).float()
    embeddings = (token_vectors * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    return embeddings.cpu().tolist()


def cosine_similarity(left: str, right: str) -> float:
    import torch

    embeddings = torch.tensor(embed_sentences([left, right]))
    return float(torch.dot(embeddings[0], embeddings[1]))

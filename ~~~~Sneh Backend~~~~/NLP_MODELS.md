# Local NLP models

SafeSight can run both models locally after their first download:

- SBERT: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings)
- RoBERTa: `roberta-base` (768-dimensional mean-pooled embeddings)

The model files are stored in `models/all-MiniLM-L6-v2` and `models/roberta-base` next to the backend. Model loading is lazy, so the Flask server can start even before the model cache is ready.

## Local API links

- `GET /api/nlp/health` — SBERT cache status
- `POST /api/nlp/embed` — SBERT embeddings: `{ "sentences": ["text"] }`
- `POST /api/nlp/similarity` — SBERT similarity: `{ "sentence_a": "text", "sentence_b": "text" }`
- `GET /api/nlp/roberta/health` — RoBERTa cache status
- `POST /api/nlp/roberta/embed` — RoBERTa embeddings: `{ "sentences": ["text"] }`
- `POST /api/nlp/roberta/similarity` — RoBERTa similarity: `{ "sentence_a": "text", "sentence_b": "text" }`

All calls use `http://localhost:5000` while the backend runs locally.

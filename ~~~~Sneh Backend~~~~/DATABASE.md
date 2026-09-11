# SafeSight database

The backend uses SQLite and creates `safesight.db` beside `app.py` on first startup. The database file is ignored by Git so local inspection history stays on the machine running the service.

## Tables

### `analyses`

Stores every successful image or video inspection with its `media_type`, original `filename`, risk percentage, risk level, hazards, explanation, percentage risk factors, detected objects, metadata, and timestamp. The website is intentionally open-access for the current demonstration.

## API routes

- `GET /api/analyses` returns saved inspection history.
- `POST /analyze` analyzes an image and saves the result.
- `POST /analyze-video` samples a video, analyzes the highest-risk frame, and saves the result.

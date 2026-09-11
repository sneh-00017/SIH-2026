# SafeSight deployment

The application has two services:

- `frontend`: Vite/React static site
- `~~~~Sneh Backend~~~~`: Flask API with SQLite analysis storage

## Deploy the backend on Render

1. Create a new Render **Web Service** from this repository.
2. Set **Root Directory** to `~~~~Sneh Backend~~~~`.
3. Set **Build Command** to `pip install -r requirements.txt`.
4. Set **Start Command** to `gunicorn --bind 0.0.0.0:$PORT app:app`.
5. Deploy and copy the HTTPS service URL, for example `https://safesight-api.onrender.com`.

The SQLite file is local to the service filesystem. For a serious production deployment, replace SQLite with managed PostgreSQL because some hosting services can reset local files during redeploys.

## Deploy the frontend on Vercel

1. Import the repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Set the build command to `npm run build`.
4. Set the output directory to `dist`.
5. Add this environment variable:

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN
```

Use the actual Render backend URL without a trailing slash. Deploy again. Vercel will provide the shareable HTTPS website link.

The frontend includes SPA fallback rules in `frontend/vercel.json` and `frontend/public/_redirects`, so refreshing `/dashboard`, `/analysis`, `/video`, or `/history` serves the React application instead of returning a 404.

## Local phone testing

Run `start_safesight.bat`, find the computer IPv4 address with `ipconfig`, and open `http://YOUR-COMPUTER-IP:5179/` on a phone using the same Wi-Fi.

## Risk percentage meaning

The displayed risk percentage is a normalized heuristic:

```text
active hazard weights / maximum configured hazard weight * 100
```

Each factor percentage uses the same maximum denominator, so the factor percentages add up to the displayed risk score. It is an explainable safety score, not a calibrated probability of injury or fatality. The API returns `score_basis` with the active and maximum weights used for each result.

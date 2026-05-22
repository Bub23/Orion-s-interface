# Orion's Interface

Local AI command center for Bub Outlaw, Sound Savage AI, Truth Exposed AI, and the OutlawAI infrastructure stack.

## Current App

- Framework: Flask
- Main app entrypoint: `web_app.py`
- Primary UI route: `/`
- Dashboard route: `/dashboard`
- Chat endpoint: `/api/chat`
- Status endpoint: `/api/status`
- Health endpoint: `/api/health`
- Memory sidebar endpoint: `/api/memories/sidebar`
- Voice routes: `/api/voice/transform`, `/api/voice/status/<job_id>`
- Default port: `8000`
- Production server: Gunicorn

## Environment

Create a local `.env` from the example file:

```bash
cp .env.example .env
```

Required for live AI responses:

```bash
NVIDIA_API_KEY=your_real_key
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
```

Optional integrations:

```bash
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_REDIRECT_URI=
YOUTUBE_API_KEY=
FACEBOOK_APP_ID=
```

## Run Locally

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python web_app.py
```

Open:

```text
http://localhost:8000
```

## Build/Run With Gunicorn

Gunicorn is the production server used inside Docker:

```bash
gunicorn --workers 2 --bind 0.0.0.0:8000 web_app:app
```

On native Windows, use `python web_app.py` for local development because Gunicorn is Unix-oriented.

## Optional RVC Voice Stack

The default install keeps the dashboard fast and Docker-friendly. Install the heavier voice/RVC dependencies only on a machine prepared for local audio model execution:

```bash
python -m pip install -r requirements-rvc.txt
```

The voice API route remains registered without the RVC stack; conversion reports failures if model/runtime dependencies are missing.

## Docker

Build and run:

```bash
docker compose up --build
```

Run in the background:

```bash
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f web
```

The container exposes:

```text
http://localhost:8000
```

Persistent local folders:

- `memories/`
- `chatgpt_exports/`
- `storage/`

## Notes

- This repo is Python/Flask, not npm-based; there is no `package.json`, `npm install`, or `npm run build` command at the root.
- `run.py` starts an older Sound Savage dashboard path on port `5000`; the Orion Command Center uses `web_app.py` on port `8000`.
- The AI command input works without crashing when `NVIDIA_API_KEY` is missing, but live model responses require the key.

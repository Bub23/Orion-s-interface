# Orion's Interface

Local AI command center for Bub Outlaw, Sound Savage AI, Truth Exposed AI, and the OutlawAI infrastructure stack.

## Current App

- Framework: Flask
- Main app entrypoint: `web_app.py`
- Primary UI route: `/`
- Dashboard route: `/dashboard`
- Chat endpoint: `/api/chat`
- Content endpoints: `/api/content/create`, `/api/content/history`, `/api/content/platform-pack`
- Campaign endpoints: `/api/campaign/create`, `/api/campaign/history`, `/api/campaign/<id>`
- Lead draft endpoints: `/api/leads/draft-message`, `/api/leads/save`, `/api/leads/history`
- Meta draft endpoints: `/api/meta/status`, `/api/meta/test`, `/api/meta/create-facebook-draft`, `/api/meta/create-instagram-draft`, `/api/meta/queue-post`
- YouTube draft endpoints: `/api/youtube/status`, `/api/youtube/create-video-draft`, `/api/youtube/queue-upload-draft`
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
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_BUSINESS_ID=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
YOUTUBE_CLIENT_SECRET_FILE=
YOUTUBE_CHANNEL_ID=
```

Keep `.env` local only. Do not commit `.env`, access tokens, app secrets, refresh tokens, page IDs tied to private accounts, or copied API responses containing credentials.

For future YouTube setup, put the Google OAuth client JSON somewhere local and private, then set only its path:

```env
YOUTUBE_CLIENT_SECRET_FILE=C:\path\to\client_secret.json
```

Do not commit the OAuth JSON file. Orion does not read, copy, or upload with that file yet.

## Run Locally

Operator launch:

```text
Double-click START_ORION.bat
```

The launcher runs preflight, starts Flask, and opens the dashboard.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python web_app.py
```

Required verification commands:

```powershell
python startup_preflight.py
python test_content_engine.py
python verify_setup.py
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
- `data/content_history.json`
- `data/campaign_history.json`
- `data/lead_history.json`
- `data/meta_queue.json`
- `data/youtube_queue.json`

## Notes

- This repo is Python/Flask, not npm-based; there is no `package.json`, `npm install`, or `npm run build` command at the root.
- `run.py` starts an older Sound Savage dashboard path on port `5000`; the Orion Command Center uses `web_app.py` on port `8000`.
- `.env` is required for live provider keys and is never committed.
- If Orion shows AI offline, add `NVIDIA_API_KEY` or `OPENAI_API_KEY` to `.env`.
- The AI command input works without crashing when provider keys are missing, but live model responses require `NVIDIA_API_KEY` or `OPENAI_API_KEY`.
- Empire Ops is draft-only. Campaigns and lead messages are saved for manual review and copy/paste; no automatic posting, scraping, or DMs are enabled.
- Meta integration is draft-only. Facebook and Instagram drafts enter `manual_review`; Orion does not publish to Meta automatically yet.
- YouTube integration is draft-only. Video drafts and upload queue items enter `manual_review`; Orion does not run OAuth or upload videos yet.

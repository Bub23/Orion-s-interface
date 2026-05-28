import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from uuid import uuid4

import requests

try:
    import certifi
except Exception:
    certifi = None


YOUTUBE_QUEUE_PATH = "data/youtube_queue.json"
OAUTH_CALLBACK_PATH = "data/oauth_callback.json"
YOUTUBE_TOKEN_STATUS_PATH = "data/youtube_token_status.json"
YOUTUBE_OAUTH_STATE_PATH = "data/youtube_oauth_state.json"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
YOUTUBE_REDIRECT_URI = "http://localhost:8000/oauth/callback"
YOUTUBE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _youtube_env():
    return {
        "YOUTUBE_CLIENT_SECRET_FILE": os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "").strip(),
        "YOUTUBE_CLIENT_ID": os.getenv("YOUTUBE_CLIENT_ID", "").strip(),
        "YOUTUBE_CLIENT_SECRET": os.getenv("YOUTUBE_CLIENT_SECRET", "").strip(),
        "YOUTUBE_REFRESH_TOKEN": os.getenv("YOUTUBE_REFRESH_TOKEN", "").strip(),
        "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID", "").strip(),
    }


def _ensure_queue():
    os.makedirs(os.path.dirname(YOUTUBE_QUEUE_PATH), exist_ok=True)
    if not os.path.exists(YOUTUBE_QUEUE_PATH):
        with open(YOUTUBE_QUEUE_PATH, "w") as f:
            json.dump({"version": "1.0", "queue": []}, f, indent=2)


def _read_queue():
    _ensure_queue()
    try:
        with open(YOUTUBE_QUEUE_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", "queue": []}
    data.setdefault("queue", [])
    return data


def _write_queue(data):
    _ensure_queue()
    with open(YOUTUBE_QUEUE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _write_json(path, data):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2)


def _load_oauth_client_config(secret_file):
    path = Path(secret_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if not path.exists():
        raise RuntimeError("YouTube OAuth client secret file missing")

    data = json.loads(path.read_text(encoding="utf-8"))
    config = data.get("installed") or data.get("web") or {}
    client_id = str(config.get("client_id") or "").strip()
    client_secret = str(config.get("client_secret") or "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("YouTube OAuth client config is incomplete")
    return client_id, client_secret


def _youtube_client_id():
    env = _youtube_env()
    if env["YOUTUBE_CLIENT_ID"]:
        return env["YOUTUBE_CLIENT_ID"]
    if env["YOUTUBE_CLIENT_SECRET_FILE"]:
        client_id, _ = _load_oauth_client_config(env["YOUTUBE_CLIENT_SECRET_FILE"])
        return client_id
    raise RuntimeError("YOUTUBE_CLIENT_ID missing")


def create_youtube_oauth_url():
    client_id = _youtube_client_id()
    state = secrets.token_urlsafe(32)
    state_payload = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "state": state,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "scope": YOUTUBE_OAUTH_SCOPES,
    }
    _write_json(YOUTUBE_OAUTH_STATE_PATH, state_payload)
    query = urlencode({
        "client_id": client_id,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(YOUTUBE_OAUTH_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    })
    return {
        "auth_url": f"{GOOGLE_AUTH_URL}?{query}",
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "state_saved": True,
    }


def _update_env_value(key, value):
    env_path = Path(__file__).resolve().parent / ".env"
    lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines() if env_path.exists() else []
    updated = False
    for index, raw in enumerate(lines):
        if raw.strip().startswith("#") or "=" not in raw:
            continue
        current_key = raw.split("=", 1)[0].strip()
        if current_key == key:
            lines[index] = f"{key}={value}"
            updated = True
            break
    if not updated:
        lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.environ[key] = value


def _token_status_payload(status, detail="", response_data=None):
    env = _youtube_env()
    payload = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "status": status,
        "detail": detail,
        "client_id_set": bool(env["YOUTUBE_CLIENT_ID"]),
        "channel_id_set": bool(env["YOUTUBE_CHANNEL_ID"]),
        "client_secret_file_path_set": bool(env["YOUTUBE_CLIENT_SECRET_FILE"]),
        "refresh_token_set": bool(env["YOUTUBE_REFRESH_TOKEN"]),
    }
    if response_data:
        payload["token_type"] = response_data.get("token_type", "")
        payload["scope"] = response_data.get("scope", "")
        payload["expires_in"] = response_data.get("expires_in", 0)
        payload["refresh_token_received"] = bool(response_data.get("refresh_token"))
    return payload


def get_youtube_token_status():
    data = _read_json(YOUTUBE_TOKEN_STATUS_PATH, {})
    env = _youtube_env()
    return {
        "status_file_exists": bool(data),
        "status": data.get("status", "missing"),
        "detail": data.get("detail", ""),
        "updated_at": data.get("updated_at", ""),
        "client_id_set": bool(env["YOUTUBE_CLIENT_ID"]),
        "channel_id_set": bool(env["YOUTUBE_CHANNEL_ID"]),
        "client_secret_file_path_set": bool(env["YOUTUBE_CLIENT_SECRET_FILE"]),
        "refresh_token_set": bool(env["YOUTUBE_REFRESH_TOKEN"]),
        "token_type": data.get("token_type", ""),
        "scope": data.get("scope", ""),
        "expires_in": data.get("expires_in", 0),
    }


def exchange_youtube_oauth_code():
    env = _youtube_env()
    if not env["YOUTUBE_CLIENT_SECRET_FILE"]:
        raise RuntimeError("YOUTUBE_CLIENT_SECRET_FILE missing")

    callback = _read_json(OAUTH_CALLBACK_PATH, {})
    result = callback.get("result") if isinstance(callback.get("result"), dict) else {}
    if result.get("error"):
        raise RuntimeError("OAuth callback contains an error")
    code = str(result.get("code") or "").strip()
    if not code:
        raise RuntimeError("OAuth callback code missing")

    client_id, client_secret = _load_oauth_client_config(env["YOUTUBE_CLIENT_SECRET_FILE"])
    redirect_uri = str(result.get("redirect_uri") or "http://localhost:8000/oauth/callback").strip()
    request_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    try:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data=request_data,
            timeout=30,
            verify=certifi.where() if certifi else True,
        )
    except requests.RequestException as error:
        status = _token_status_payload("failed", "Google token exchange request failed")
        _write_json(YOUTUBE_TOKEN_STATUS_PATH, status)
        raise RuntimeError("Google token exchange request failed") from error
    response_data = response.json() if response.content else {}
    if not response.ok:
        status = _token_status_payload("failed", "Google token exchange failed", response_data)
        _write_json(YOUTUBE_TOKEN_STATUS_PATH, status)
        raise RuntimeError("Google token exchange failed")

    refresh_token = str(response_data.get("refresh_token") or "").strip()
    if not refresh_token:
        status = _token_status_payload("failed", "No refresh token returned", response_data)
        _write_json(YOUTUBE_TOKEN_STATUS_PATH, status)
        raise RuntimeError("No refresh token returned")

    _update_env_value("YOUTUBE_CLIENT_ID", client_id)
    _update_env_value("YOUTUBE_REFRESH_TOKEN", refresh_token)
    status = _token_status_payload("ok", "Refresh token saved", response_data)
    status["refresh_token_set"] = True
    _write_json(YOUTUBE_TOKEN_STATUS_PATH, status)
    return status


def validate_youtube_env():
    env = _youtube_env()
    required = [
        "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CHANNEL_ID",
        "YOUTUBE_CLIENT_SECRET_FILE",
        "YOUTUBE_REFRESH_TOKEN",
    ]
    missing = [key for key in required if not env[key]]
    return {
        "configured": not missing,
        "missing": missing,
        "client_secret_file_path_set": bool(env["YOUTUBE_CLIENT_SECRET_FILE"]),
        "refresh_token_set": bool(env["YOUTUBE_REFRESH_TOKEN"]),
        "client_id_set": bool(env["YOUTUBE_CLIENT_ID"]),
        "channel_id_set": bool(env["YOUTUBE_CHANNEL_ID"]),
    }


def get_youtube_status():
    status = validate_youtube_env()
    queue = _read_queue()["queue"]
    return {
        "provider": "youtube",
        "configured": status["configured"],
        "missing": status["missing"],
        "client_id_set": status["client_id_set"],
        "client_secret_file_path_set": status["client_secret_file_path_set"],
        "refresh_token_set": status["refresh_token_set"],
        "channel_id_set": status["channel_id_set"],
        "queue_total": len(queue),
        "queue": sorted(queue, key=lambda item: item.get("created_at", ""), reverse=True)[:20],
        "mode": "manual_review",
    }


def create_youtube_video_draft(payload):
    topic = str(payload.get("topic") or payload.get("title") or "Orion video").strip()
    offer = str(payload.get("offer") or "Orion-powered execution").strip()
    audience = str(payload.get("audience") or "operators and business owners").strip()
    video_type = str(payload.get("video_type") or "short").strip()
    return {
        "platform": "youtube",
        "content_type": "youtube_video_draft",
        "status": "draft",
        "review_status": "manual_review",
        "video_type": video_type,
        "title": f"{topic} | Orion",
        "description": (
            f"For {audience}: {offer}.\n\n"
            "This is a manual-review YouTube draft. Upload is not enabled yet."
        ),
        "script": (
            f"Hook: Most people are wasting time on {topic}.\n"
            f"Body: Orion turns {offer} into a faster execution path for {audience}.\n"
            "CTA: Review the draft, tighten the proof, then manually approve before any upload."
        ),
        "tags": ["OrionInterface", "OutlawAI", "SoundSavageAI"],
    }


def queue_youtube_upload_draft(payload):
    draft = payload.get("draft") if isinstance(payload.get("draft"), dict) else {}
    item = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "platform": "youtube",
        "content_type": str(payload.get("content_type") or draft.get("content_type") or "youtube_upload_draft"),
        "title": str(payload.get("title") or draft.get("title") or "YouTube Draft").strip(),
        "body": payload.get("body") or draft.get("description") or "",
        "script": payload.get("script") or draft.get("script") or "",
        "status": "draft",
        "review_status": "manual_review",
        "approved": False,
        "metadata": {
            "source": "youtube_integration",
            "video_type": payload.get("video_type") or draft.get("video_type") or "short",
            "channel_id_set": bool(_youtube_env()["YOUTUBE_CHANNEL_ID"]),
            "client_secret_file_path_set": bool(_youtube_env()["YOUTUBE_CLIENT_SECRET_FILE"]),
        },
    }
    data = _read_queue()
    data["queue"].append(item)
    _write_queue(data)
    return item

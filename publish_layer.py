import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests


HISTORY_PATH = "data/publish_history.json"
GRAPH_URL = "https://graph.facebook.com/v20.0"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def _env(name):
    return os.getenv(name, "").strip()


def _load_youtube_client_config():
    secret_file = _env("YOUTUBE_CLIENT_SECRET_FILE")
    if not secret_file:
        return {}

    path = Path(secret_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data.get("installed") or data.get("web") or {}


def _youtube_publish_credentials():
    client_config = _load_youtube_client_config()
    client_id = _env("YOUTUBE_CLIENT_ID") or str(client_config.get("client_id") or "").strip()
    client_secret = _env("YOUTUBE_CLIENT_SECRET") or str(client_config.get("client_secret") or "").strip()
    refresh_token = _env("YOUTUBE_REFRESH_TOKEN")
    channel_id = _env("YOUTUBE_CHANNEL_ID")
    missing = []
    if not client_id:
        missing.append("YOUTUBE_CLIENT_ID")
    if not client_secret:
        missing.append("YOUTUBE_CLIENT_SECRET")
    if not refresh_token:
        missing.append("YOUTUBE_REFRESH_TOKEN")
    if not channel_id:
        missing.append("YOUTUBE_CHANNEL_ID")
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "channel_id": channel_id,
        "missing": missing,
        "client_secret_source": "env" if _env("YOUTUBE_CLIENT_SECRET") else "client_secret_file" if client_secret else "missing",
    }


def _ensure_history():
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f:
            json.dump({"version": "1.0", "publishes": []}, f, indent=2)


def _read_history():
    _ensure_history()
    try:
        with open(HISTORY_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", "publishes": []}
    data.setdefault("publishes", [])
    return data


def save_publish_result(platform, source, item_id, success, response=None, error=None):
    data = _read_history()
    record = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "platform": platform,
        "source": source,
        "source_id": item_id,
        "success": bool(success),
        "response": response or {},
        "error": str(error) if error else "",
    }
    data["publishes"].append(record)
    with open(HISTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return record


def publish_status():
    history = _read_history()["publishes"]
    youtube_credentials = _youtube_publish_credentials()
    youtube_missing = youtube_credentials["missing"]
    youtube_ready = not youtube_missing
    return {
        "facebook_configured": bool(_env("META_ACCESS_TOKEN") and _env("FACEBOOK_PAGE_ID")),
        "instagram_configured": bool(_env("META_ACCESS_TOKEN") and _env("INSTAGRAM_BUSINESS_ID")),
        "youtube_configured": youtube_ready,
        "youtube_ready": youtube_ready,
        "youtube_missing": youtube_missing,
        "youtube_client_id_set": bool(youtube_credentials["client_id"]),
        "youtube_client_secret_set": bool(youtube_credentials["client_secret"]),
        "youtube_client_secret_source": youtube_credentials["client_secret_source"],
        "youtube_refresh_token_set": bool(youtube_credentials["refresh_token"]),
        "youtube_channel_id_set": bool(youtube_credentials["channel_id"]),
        "history_total": len(history),
    }


def publish_history():
    history = sorted(_read_history()["publishes"], key=lambda item: item.get("created_at", ""), reverse=True)
    return {"total": len(history), "publishes": history}


def _graph_post(path, data):
    token = _env("META_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN missing")
    payload = dict(data)
    payload["access_token"] = token
    response = requests.post(f"{GRAPH_URL}/{path}", data=payload, timeout=30)
    safe = response.json() if response.content else {}
    response.raise_for_status()
    return safe


def publish_facebook(body):
    page_id = _env("FACEBOOK_PAGE_ID")
    if not page_id:
        raise RuntimeError("FACEBOOK_PAGE_ID missing")
    if not body:
        raise RuntimeError("No Facebook post body available")
    result = _graph_post(f"{page_id}/feed", {"message": body})
    return {"platform_post_id": result.get("id", ""), "raw": result}


def publish_instagram(caption, media_url=None):
    ig_id = _env("INSTAGRAM_BUSINESS_ID")
    if not ig_id:
        raise RuntimeError("INSTAGRAM_BUSINESS_ID missing")
    if not media_url:
        raise RuntimeError("Instagram publishing requires media_url")
    create_result = _graph_post(f"{ig_id}/media", {"image_url": media_url, "caption": caption or ""})
    creation_id = create_result.get("id")
    if not creation_id:
        raise RuntimeError("Instagram media container was not created")
    publish_result = _graph_post(f"{ig_id}/media_publish", {"creation_id": creation_id})
    return {"platform_post_id": publish_result.get("id", ""), "container_id": creation_id, "raw": publish_result}


def _youtube_access_token():
    credentials = _youtube_publish_credentials()
    if credentials["missing"]:
        raise RuntimeError(f"YouTube OAuth env vars missing: {', '.join(credentials['missing'])}")
    response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "refresh_token": credentials["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    data = response.json() if response.content else {}
    response.raise_for_status()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("YouTube access token unavailable")
    return token


def publish_youtube(title, description, video_path, tags=None):
    if not video_path:
        raise RuntimeError("video_path is required for YouTube upload")
    path = Path(video_path)
    if not path.exists():
        raise RuntimeError("video_path does not exist")
    access_token = _youtube_access_token()
    metadata = {
        "snippet": {
            "title": title or "Orion Upload",
            "description": description or "",
            "tags": tags or [],
            "categoryId": "22",
        },
        "status": {"privacyStatus": "private"},
    }
    response = requests.post(
        f"{YOUTUBE_UPLOAD_URL}?part=snippet,status&uploadType=multipart",
        headers={"Authorization": f"Bearer {access_token}"},
        files={
            "metadata": ("metadata.json", json.dumps(metadata), "application/json; charset=UTF-8"),
            "media": (path.name, path.open("rb"), "application/octet-stream"),
        },
        timeout=120,
    )
    data = response.json() if response.content else {}
    response.raise_for_status()
    return {"platform_post_id": data.get("id", ""), "raw": {"id": data.get("id", ""), "kind": data.get("kind", "")}}


def publish_comment_reply(comment_id, message):
    if not comment_id:
        raise RuntimeError("comment_id is required")
    if not message:
        raise RuntimeError("reply message is required")
    result = _graph_post(f"{comment_id}/comments", {"message": message})
    return {"platform_reply_id": result.get("id", ""), "raw": result}

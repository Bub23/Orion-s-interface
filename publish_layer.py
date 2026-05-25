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
    youtube_ready = bool(
        _env("YOUTUBE_CLIENT_ID")
        and _env("YOUTUBE_CHANNEL_ID")
        and _env("YOUTUBE_CLIENT_SECRET_FILE")
        and _env("YOUTUBE_REFRESH_TOKEN")
    )
    return {
        "facebook_configured": bool(_env("META_ACCESS_TOKEN") and _env("FACEBOOK_PAGE_ID")),
        "instagram_configured": bool(_env("META_ACCESS_TOKEN") and _env("INSTAGRAM_BUSINESS_ID")),
        "youtube_configured": youtube_ready,
        "youtube_ready": youtube_ready,
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
    client_id = _env("YOUTUBE_CLIENT_ID")
    client_secret = _env("YOUTUBE_CLIENT_SECRET")
    refresh_token = _env("YOUTUBE_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError("YouTube OAuth env vars missing")
    response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
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

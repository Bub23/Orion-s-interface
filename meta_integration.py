import json
import os
from datetime import datetime
from uuid import uuid4


META_QUEUE_PATH = "data/meta_queue.json"


def _meta_env():
    return {
        "META_APP_ID": os.getenv("META_APP_ID", "").strip(),
        "META_APP_SECRET": os.getenv("META_APP_SECRET", "").strip(),
        "META_ACCESS_TOKEN": os.getenv("META_ACCESS_TOKEN", "").strip(),
        "FACEBOOK_PAGE_ID": os.getenv("FACEBOOK_PAGE_ID", "").strip(),
        "INSTAGRAM_BUSINESS_ID": os.getenv("INSTAGRAM_BUSINESS_ID", "").strip(),
    }


def _ensure_queue():
    os.makedirs(os.path.dirname(META_QUEUE_PATH), exist_ok=True)
    if not os.path.exists(META_QUEUE_PATH):
        with open(META_QUEUE_PATH, "w") as f:
            json.dump({"version": "1.0", "queue": []}, f, indent=2)


def _read_queue():
    _ensure_queue()
    try:
        with open(META_QUEUE_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", "queue": []}
    data.setdefault("queue", [])
    return data


def _write_queue(data):
    _ensure_queue()
    with open(META_QUEUE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def validate_meta_connection():
    env = _meta_env()
    missing = [key for key, value in env.items() if not value]
    return {
        "configured": not missing,
        "missing": missing,
        "facebook_ready": bool(env["META_ACCESS_TOKEN"] and env["FACEBOOK_PAGE_ID"]),
        "instagram_ready": bool(env["META_ACCESS_TOKEN"] and env["INSTAGRAM_BUSINESS_ID"]),
    }


def get_meta_status():
    status = validate_meta_connection()
    queue = _read_queue()["queue"]
    return {
        "provider": "meta",
        "configured": status["configured"],
        "facebook_ready": status["facebook_ready"],
        "instagram_ready": status["instagram_ready"],
        "missing": status["missing"],
        "queue_total": len(queue),
        "queue": sorted(queue, key=lambda item: item.get("created_at", ""), reverse=True)[:20],
        "mode": "manual_review",
    }


def create_facebook_post_draft(payload):
    topic = str(payload.get("topic") or payload.get("title") or "Facebook offer").strip()
    offer = str(payload.get("offer") or "Orion-powered execution").strip()
    audience = str(payload.get("audience") or "buyers").strip()
    return {
        "platform": "facebook",
        "content_type": "facebook_post",
        "status": "draft",
        "review_status": "manual_review",
        "post_text": (
            f"{topic}\n\n"
            f"If you're {audience} and tired of slow execution, {offer} is built for a cleaner next move.\n\n"
            "Manual review required before posting."
        ),
    }


def create_instagram_caption_draft(payload):
    topic = str(payload.get("topic") or payload.get("title") or "Instagram offer").strip()
    offer = str(payload.get("offer") or "Orion-powered execution").strip()
    audience = str(payload.get("audience") or "buyers").strip()
    return {
        "platform": "instagram",
        "content_type": "instagram_caption",
        "status": "draft",
        "review_status": "manual_review",
        "caption": (
            f"{topic}\n\n"
            f"Built for {audience}. Powered by {offer}.\n\n"
            "Review manually before posting.\n\n"
            "#OrionInterface #OutlawAI #SoundSavageAI"
        ),
    }


def queue_meta_post(payload):
    platform = str(payload.get("platform", "facebook")).strip().lower()
    body = payload.get("body") or payload.get("post_text") or payload.get("caption") or ""
    item = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "platform": platform,
        "content_type": str(payload.get("content_type", "meta_post")).strip(),
        "title": str(payload.get("title", "Meta Draft")).strip() or "Meta Draft",
        "body": body,
        "status": "draft",
        "review_status": "manual_review",
        "approved": False,
        "metadata": {
            "source": "meta_integration",
            "has_facebook_page_id": bool(_meta_env()["FACEBOOK_PAGE_ID"]),
            "has_instagram_business_id": bool(_meta_env()["INSTAGRAM_BUSINESS_ID"]),
        },
    }
    data = _read_queue()
    data["queue"].append(item)
    _write_queue(data)
    return item

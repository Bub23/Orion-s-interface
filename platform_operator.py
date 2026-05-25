import json
import os
from datetime import datetime
from uuid import uuid4


DATA_DIR = "data"
FILES = {
    "audits": os.path.join(DATA_DIR, "youtube_audits.json"),
    "media_jobs": os.path.join(DATA_DIR, "media_jobs.json"),
    "replies": os.path.join(DATA_DIR, "social_reply_drafts.json"),
    "updates": os.path.join(DATA_DIR, "platform_update_drafts.json"),
    "targets": os.path.join(DATA_DIR, "lead_target_lists.json"),
}


def _read(path, key):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"version": "1.0", key: []}, f, indent=2)
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", key: []}
    data.setdefault(key, [])
    return data


def _write(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _words(text):
    return [word.strip(".,!?:;()[]{}\"'").lower() for word in str(text).split()]


def audit_video(payload):
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    hashtags = payload.get("hashtags", [])
    if isinstance(hashtags, str):
        hashtags = [tag for tag in hashtags.split() if tag.startswith("#")]
    weak_words = [word for word in _words(title + " " + description) if len(word) > 24]
    audit = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "type": "video_audit",
        "status": "manual_review",
        "title_spelling_flags": weak_words,
        "description_spelling_flags": weak_words,
        "hashtag_quality": "good" if 3 <= len(hashtags) <= 8 else "needs tighter hashtag set",
        "suggested_title": title[:70] if title else "Clear outcome-driven title | Orion",
        "suggested_description": f"{description}\n\nManual review update draft. Add clear CTA and 3-8 relevant hashtags.".strip(),
        "shorts_version": f"Hook: {title or 'This changes the next move'}\nPoint: one clear lesson.\nCTA: follow for the next execution step.",
        "input": payload,
    }
    data = _read(FILES["audits"], "audits")
    data["audits"].append(audit)
    _write(FILES["audits"], data)
    return audit


def audit_channel(payload):
    niche = str(payload.get("niche", "AI operations")).strip()
    channel_name = str(payload.get("channel_name", "Channel")).strip()
    audit = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "type": "channel_audit",
        "status": "manual_review",
        "channel_name": channel_name,
        "recommendations": [
            f"Make the channel promise obvious for {niche}.",
            "Pin one offer-forward intro video.",
            "Group Shorts around one repeatable series.",
            "Use titles that lead with outcome, not vague branding.",
        ],
    }
    data = _read(FILES["audits"], "audits")
    data["audits"].append(audit)
    _write(FILES["audits"], data)
    return audit


def fix_draft(payload):
    fixed = audit_video(payload)
    fixed["type"] = "youtube_update_draft"
    fixed["update_draft"] = {
        "title": fixed["suggested_title"],
        "description": fixed["suggested_description"],
        "status": "manual_review",
    }
    return fixed


def create_short_pack(payload):
    topic = str(payload.get("topic") or payload.get("title") or "Orion execution").strip()
    pack = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "status": "manual_review",
        "short_title": f"{topic} in 30 seconds",
        "short_script": f"Hook: Most people overcomplicate {topic}. Point: make one clean move today. CTA: save this and execute.",
        "voiceover_script": f"Direct voiceover: {topic} needs speed, clarity, and follow-through.",
        "avatar_prompt": f"Serious Orion operator avatar explaining {topic}, dark command center style.",
        "scene_prompts": [f"Opening text hit for {topic}", "Dashboard/action proof shot", "CTA end card"],
        "captions": ["Stop overcomplicating it.", "Make one clean move.", "Execute today."],
        "thumbnail_prompt": f"High contrast thumbnail for {topic}, red black steel palette.",
        "platform_export_pack": {"youtube": "Shorts-ready", "instagram": "Reels-ready", "tiktok": "TikTok-ready"},
    }
    data = _read(FILES["media_jobs"], "jobs")
    data["jobs"].append({"id": pack["id"], "type": "short", "script": pack["short_script"], "voice_profile": "", "avatar_style": "", "status": "manual_review", "output_path": "", "created_at": pack["created_at"]})
    _write(FILES["media_jobs"], data)
    return pack


def create_media_job(payload, job_type):
    data = _read(FILES["media_jobs"], "jobs")
    job = {
        "id": str(uuid4()),
        "type": job_type,
        "script": str(payload.get("script", "")).strip(),
        "voice_profile": str(payload.get("voice_profile", "")).strip(),
        "avatar_style": str(payload.get("avatar_style", "")).strip(),
        "status": "manual_review",
        "output_path": "",
        "created_at": datetime.now().isoformat(),
    }
    data["jobs"].append(job)
    _write(FILES["media_jobs"], data)
    return job


def get_media_jobs():
    return {"jobs": _read(FILES["media_jobs"], "jobs")["jobs"]}


def platform_update_draft(payload, platform):
    data = _read(FILES["updates"], "drafts")
    draft = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "platform": platform,
        "title": str(payload.get("title", f"{platform.title()} Draft")).strip(),
        "body": str(payload.get("body") or payload.get("caption") or "").strip(),
        "content_type": f"{platform}_update_draft",
        "status": "manual_review",
    }
    data["drafts"].append(draft)
    _write(FILES["updates"], data)
    return draft


def reply_draft(payload):
    data = _read(FILES["replies"], "replies")
    reply = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "platform": str(payload.get("platform", "manual")).strip(),
        "customer_message": str(payload.get("customer_message", "")).strip(),
        "reply": f"Thanks for reaching out. Here is the direct next step: {str(payload.get('offer', 'send details for manual review')).strip()}",
        "status": "manual_review",
    }
    data["replies"].append(reply)
    _write(FILES["replies"], data)
    return reply


def target_list(payload):
    niche = str(payload.get("niche", "local business")).strip()
    location = str(payload.get("location", "local market")).strip()
    platform = str(payload.get("platform", "manual")).strip()
    item = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "niche": niche,
        "location": location,
        "platform": platform,
        "targets": [
            f"{location} {niche} owners with outdated content systems",
            f"{location} service providers missing follow-up automation",
            f"{location} creators who need short-form repurposing",
        ],
        "status": "manual_review",
    }
    data = _read(FILES["targets"], "lists")
    data["lists"].append(item)
    _write(FILES["targets"], data)
    return item


def outreach_sequence(payload):
    niche = str(payload.get("niche", "business")).strip()
    offer = str(payload.get("offer", "Orion setup sprint")).strip()
    return {
        "status": "manual_review",
        "target_profile": f"{niche} operator with clear revenue leakage from slow follow-up or weak content.",
        "outreach_script": f"Quick question: are you still handling {niche} content and follow-up manually? {offer} may tighten that up.",
        "followups": ["Wanted to make sure this did not get buried.", "Last touch. If this is not a fit, no problem."],
        "offer_angle": f"Sell {offer} as speed, clarity, and fewer missed opportunities.",
    }

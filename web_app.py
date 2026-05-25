from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import platform
import sys
from datetime import datetime
import psutil
import requests
import json
from content_engine import ContentEngine, CampaignDraftEngine, LeadDraftEngine, EmpireQueueEngine
from meta_integration import (
    validate_meta_connection,
    create_facebook_post_draft,
    create_instagram_caption_draft,
    queue_meta_post,
    get_meta_status,
    _read_queue as _read_meta_queue,
    _write_queue as _write_meta_queue,
)
from youtube_integration import (
    get_youtube_status,
    get_youtube_token_status,
    create_youtube_oauth_url,
    exchange_youtube_oauth_code,
    validate_youtube_env,
    create_youtube_video_draft,
    queue_youtube_upload_draft,
    _read_queue as _read_youtube_queue,
    _write_queue as _write_youtube_queue,
)
from revenue_engine import (
    create_offer,
    create_lead,
    get_leads,
    update_lead,
    create_followup,
    get_followups,
    mark_followup_done,
    revenue_report,
)
from daily_ops import (
    create_task,
    get_tasks,
    complete_task,
    reset_day,
    set_content_goals,
    get_content_goals,
    log_revenue,
    revenue_today,
)
from platform_operator import (
    audit_video,
    audit_channel,
    fix_draft,
    create_short_pack,
    create_media_job,
    get_media_jobs,
    platform_update_draft,
    reply_draft,
    target_list,
    outreach_sequence,
)
from publish_layer import (
    publish_status,
    publish_history,
    save_publish_result,
    publish_facebook,
    publish_instagram,
    publish_youtube,
    publish_comment_reply,
)

try:
    import GPUtil
except Exception:
    GPUtil = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


load_dotenv()

app = Flask(__name__)
CORS(app)
content_engine = ContentEngine()
campaign_engine = CampaignDraftEngine()
lead_engine = LeadDraftEngine()
empire_queue = EmpireQueueEngine()
EXPORT_PACK_PATH = "data/export_pack_history.json"
OAUTH_CALLBACK_PATH = "data/oauth_callback.json"

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.WARNING)

APP_PORT = int(os.getenv("APP_PORT", "8000"))
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

NOISY_ROUTES = {
    "/api/status",
    "/api/health",
    "/api/memories/sidebar",
    "/api/system-metrics",
    "/api/gpu",
    "/api/content/history",
    "/api/campaign/history",
    "/api/leads/history",
    "/api/empire/posting-queue",
    "/api/meta/status",
    "/api/youtube/status",
    "/api/approval-queue",
    "/api/revenue/leads",
    "/api/revenue/followups",
    "/api/revenue/report",
    "/api/daily/tasks",
    "/api/daily/content-goals",
    "/api/daily/revenue-today",
    "/api/publish/status",
    "/api/publish/history",
}

orion_system_prompt = """
You are Orion, Bub Outlaw's local AI command center.

Rules:
- Be blunt, accurate, loyal, and useful.
- Never invent system stats.
- Use only available API/status/metrics context when discussing system health.
- If CPU, RAM, disk, GPU, network, Docker, or app status is not provided, say it is not currently instrumented.
- Help build Orion, Sound Savage AI, Truth Exposed AI, music systems, automation, and infrastructure.
- No fake dates. No fake capabilities. No fake logs.
- Keep answers practical and action-ready.
"""


def get_ai_ready():
    return bool(NVIDIA_API_KEY or OPENAI_API_KEY)


def _reload_runtime_env():
    load_dotenv(override=True)


def _env_value(name):
    return os.getenv(name, "").strip()


def _platform_status(required_keys):
    missing = [key for key in required_keys if not _env_value(key)]
    return {
        "ready": not missing,
        "missing": missing,
    }


def get_platform_full_status():
    _reload_runtime_env()
    return {
        "youtube": _platform_status([
            "YOUTUBE_CLIENT_ID",
            "YOUTUBE_CHANNEL_ID",
            "YOUTUBE_CLIENT_SECRET_FILE",
            "YOUTUBE_REFRESH_TOKEN",
        ]),
        "meta": _platform_status([
            "META_ACCESS_TOKEN",
            "FACEBOOK_PAGE_ID",
            "INSTAGRAM_BUSINESS_ID",
        ]),
    }


def _save_oauth_callback_result(result):
    os.makedirs(os.path.dirname(OAUTH_CALLBACK_PATH), exist_ok=True)
    payload = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "result": result,
    }
    with open(OAUTH_CALLBACK_PATH, "w", encoding="utf-8") as callback_file:
        json.dump(payload, callback_file, indent=2)


def _oauth_callback_page(success, message):
    title = "OAuth Callback Saved" if success else "OAuth Callback Failed"
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head><meta charset=\"utf-8\"><title>Orion OAuth Callback</title>"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<style>body{font-family:Arial,sans-serif;margin:40px;line-height:1.5;max-width:720px}"
        ".status{font-weight:700}</style></head>"
        "<body>"
        f"<h1>{title}</h1>"
        f"<p class=\"status\">{message}</p>"
        "<p>You can close this window and return to Orion.</p>"
        "</body></html>"
    )


def get_memory_status():
    return {
        "total_conversations": 0,
        "total_facts": 0,
        "memory_file_size": 0
    }


def get_gpu_payload():
    if GPUtil is None:
        return {
            "available": False,
            "status": "not_installed",
            "message": "GPUtil package is not installed."
        }

    try:
        gpus = GPUtil.getGPUs()

        if not gpus:
            return {
                "available": False,
                "status": "not_detected",
                "message": "No NVIDIA GPU detected by GPUtil."
            }

        gpu_list = []

        for gpu in gpus:
            gpu_list.append({
                "id": gpu.id,
                "name": gpu.name,
                "load_percent": round(gpu.load * 100, 1),
                "memory_total_mb": round(gpu.memoryTotal, 1),
                "memory_used_mb": round(gpu.memoryUsed, 1),
                "memory_free_mb": round(gpu.memoryFree, 1),
                "memory_used_percent": round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1) if gpu.memoryTotal else 0,
                "temperature_c": gpu.temperature
            })

        primary = gpu_list[0]

        return {
            "available": True,
            "status": "online",
            "primary": primary,
            "gpus": gpu_list
        }

    except Exception as error:
        return {
            "available": False,
            "status": "error",
            "message": str(error)
        }


def get_system_metrics_payload():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    gpu = get_gpu_payload()

    return {
        "status": "online",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory": {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "used_percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "used_percent": disk.percent
        },
        "gpu": gpu,
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    }


def call_nvidia(message, context):
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")

    url = f"{NVIDIA_BASE_URL}/chat/completions"

    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": orion_system_prompt
            },
            {
                "role": "system",
                "content": f"Current real local context:\n{context}"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.35,
        "top_p": 0.9,
        "max_tokens": 900,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_openai(message, context):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    if OpenAI is None:
        raise RuntimeError("OpenAI package is not installed.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": orion_system_prompt
            },
            {
                "role": "system",
                "content": f"Current real local context:\n{context}"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.35,
        max_tokens=900
    )

    return response.choices[0].message.content


def fallback_response(message, context, error_text):
    return f"""ORION LOCAL FALLBACK

I received the command:

{message}

Real local context available:
{context}

AI provider call failed:
{error_text}

Operational note:
The dashboard, Flask backend, health endpoint, status endpoint, system metrics endpoint, GPU metrics route, and Docker container can still run locally. The AI provider key, model endpoint, or network route needs correction before live model responses work.
"""


def generate_empire_asset(asset_type, payload):
    topic = str(payload.get("topic") or payload.get("title") or payload.get("offer") or "Bub Outlaw empire offer").strip()
    platform = str(payload.get("platform", "multi-platform")).strip()
    tone = str(payload.get("tone", "outlaw, blunt, professional")).strip()
    audience = str(payload.get("audience", "buyers who need fast execution")).strip()
    offer = str(payload.get("offer", "Orion-powered execution")).strip()

    prompt = (
        f"Generate a {asset_type} for Orion Interface. Topic: {topic}. "
        f"Audience: {audience}. Offer: {offer}. Platform: {platform}. Tone: {tone}. "
        "Return concise, revenue-focused draft copy only. No auto-posting claims."
    )

    context = {
        "app": "Orion Interface",
        "workflow": "draft/manual_review only",
        "no_auto_posting": True,
    }

    provider = "local_fallback"
    try:
        if NVIDIA_API_KEY:
            generated = call_nvidia(prompt, str(context))
            provider = "nvidia"
        else:
            raise RuntimeError("NVIDIA_API_KEY is not configured.")
    except Exception as error:
        generated = (
            f"{asset_type.upper()} DRAFT\n"
            f"Topic: {topic}\n"
            f"Audience: {audience}\n"
            f"Offer: {offer}\n"
            f"Platform: {platform}\n"
            f"Tone: {tone}\n\n"
            "Hook: Stop letting the opportunity sit cold.\n"
            f"Body: {offer} gives {audience} a direct path to move faster with less guessing.\n"
            "CTA: Review this draft manually, tighten the details, then post only after approval."
        )

    return {
        "id": None,
        "created_at": datetime.now().isoformat(),
        "asset_type": asset_type,
        "provider": provider,
        "model": NVIDIA_MODEL if provider == "nvidia" else "local_fallback",
        "status": "draft",
        "review_status": "manual_review",
        "platform": platform,
        "generated": generated,
        "input": payload,
    }


def empire_generation_response(asset_type):
    payload = request.get_json(silent=True) or {}
    result = generate_empire_asset(asset_type, payload)
    saved = empire_queue.create_item({
        "title": payload.get("title") or f"{asset_type} draft",
        "platform": result["platform"],
        "content_type": asset_type,
        "body": result["generated"],
        "metadata": {
            "provider": result["provider"],
            "model": result["model"],
            "input": payload,
        },
    })
    result["id"] = saved["id"]
    result["queue_item"] = saved
    return jsonify(result), 201


@app.before_request
def log_request():
    if request.path not in NOISY_ROUTES:
        logger.info("%s %s", request.method, request.path)


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "online",
        "app": "Orion Interface",
        "ai_ready": get_ai_ready(),
        "model": NVIDIA_MODEL if NVIDIA_API_KEY else OPENAI_MODEL if OPENAI_API_KEY else "not configured",
        "port": APP_PORT,
        "tiktok": "NOT CONFIGURED",
        "voice_route": "registered",
        "gpu_route": "registered",
        "memory": get_memory_status()
    })


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "healthy",
        "server": "running",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/memories/sidebar", methods=["GET"])
def memories_sidebar():
    return jsonify({
        "total_memories": 0,
        "categories": {
            "Recent Facts": []
        }
    })


@app.route("/api/system-metrics", methods=["GET"])
def system_metrics():
    try:
        return jsonify(get_system_metrics_payload())
    except Exception as error:
        logger.exception("System metrics failed")
        return jsonify({
            "status": "error",
            "error": str(error)
        }), 500


@app.route("/api/gpu", methods=["GET"])
def gpu_metrics():
    try:
        return jsonify(get_gpu_payload())
    except Exception as error:
        logger.exception("GPU metrics failed")
        return jsonify({
            "available": False,
            "status": "error",
            "message": str(error)
        }), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "error": "Message is required."
            }), 400

        status_context = {
            "status": {
                "app": "Orion Interface",
                "status": "online",
                "ai_ready": get_ai_ready(),
                "model": NVIDIA_MODEL if NVIDIA_API_KEY else OPENAI_MODEL if OPENAI_API_KEY else "not configured",
                "port": APP_PORT,
                "voice_route": "registered",
                "gpu_route": "registered",
                "tiktok": "NOT CONFIGURED"
            },
            "health": {
                "status": "healthy",
                "server": "running"
            },
            "system_metrics": get_system_metrics_payload(),
            "memory": get_memory_status()
        }

        context_text = str(status_context)

        try:
            if NVIDIA_API_KEY:
                answer = call_nvidia(message, context_text)
                provider = "nvidia"
            elif OPENAI_API_KEY:
                answer = call_openai(message, context_text)
                provider = "openai"
            else:
                raise RuntimeError("No NVIDIA_API_KEY or OPENAI_API_KEY configured.")

            return jsonify({
                "response": answer,
                "provider": provider,
                "model": NVIDIA_MODEL if provider == "nvidia" else OPENAI_MODEL
            })

        except Exception as provider_error:
            logger.exception("AI provider call failed")

            return jsonify({
                "response": fallback_response(message, context_text, str(provider_error)),
                "provider": "local_fallback",
                "model": "none"
            })

    except Exception as error:
        logger.exception("Chat route failed")

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/content/create", methods=["POST"])
def content_create():
    """Create a new content draft."""
    try:
        data = request.get_json(silent=True) or {}
        content = str(data.get("content", "")).strip()
        title = data.get("title", "").strip()
        platforms = data.get("platforms")

        if not content:
            return jsonify({"error": "Content is required"}), 400

        result = content_engine.create_content(
            content=content,
            title=title if title else None,
            platforms=platforms if isinstance(platforms, list) else None
        )

        if "error" in result:
            return jsonify(result), 400

        logger.info("Content created: %s", result["draft_id"])
        return jsonify(result), 201

    except Exception as error:
        logger.exception("Content creation failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/save", methods=["POST"])
def content_save():
    """Save a content draft (update or create)."""
    try:
        data = request.get_json(silent=True) or {}
        draft_id = data.get("draft_id")
        content = str(data.get("content", "")).strip()
        title = data.get("title", "").strip()

        if not content:
            return jsonify({"error": "Content is required"}), 400

        if draft_id:
            updated = content_engine.storage.update_draft(
                draft_id=draft_id,
                content=content,
                title=title if title else None
            )

            if not updated:
                return jsonify({"error": f"Draft not found: {draft_id}"}), 404

            logger.info("Content updated: %s", draft_id)
            return jsonify({
                "success": True,
                "draft_id": draft_id,
                "updated_at": updated["updated_at"]
            })
        else:
            result = content_engine.create_content(
                content=content,
                title=title if title else None
            )
            logger.info("Content saved: %s", result["draft_id"])
            return jsonify(result), 201

    except Exception as error:
        logger.exception("Content save failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/history", methods=["GET"])
def content_history():
    """Retrieve content history."""
    try:
        limit = request.args.get("limit", type=int)
        offset = request.args.get("offset", default=0, type=int)
        platform_filter = request.args.get("platform")

        if limit and limit > 100:
            limit = 100

        result = content_engine.get_content_history(
            limit=limit,
            offset=offset,
            platform_filter=platform_filter
        )

        logger.info("Content history retrieved: %d total", result["total"])
        return jsonify(result)

    except Exception as error:
        logger.exception("Content history retrieval failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/platform-pack", methods=["GET"])
def content_platform_pack():
    """Get platform-specific formatting for a draft."""
    try:
        draft_id = request.args.get("draft_id")

        if not draft_id:
            return jsonify({"error": "draft_id parameter is required"}), 400

        result = content_engine.get_platform_pack(draft_id)

        if "error" in result:
            return jsonify(result), 404

        logger.info("Platform pack generated: %s", draft_id)
        return jsonify(result)

    except Exception as error:
        logger.exception("Platform pack generation failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/search", methods=["GET"])
def content_search():
    """Search content drafts."""
    try:
        query = request.args.get("q", "").strip()

        if not query:
            return jsonify({"error": "Search query is required"}), 400

        result = content_engine.search_content(query)

        logger.info("Content search: %s - %d results", query, result["total_results"])
        return jsonify(result)

    except Exception as error:
        logger.exception("Content search failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/draft/<draft_id>", methods=["GET"])
def content_get_draft(draft_id):
    """Get a specific draft."""
    try:
        result = content_engine.get_draft_details(draft_id)

        if "error" in result:
            return jsonify(result), 404

        return jsonify(result)

    except Exception as error:
        logger.exception("Draft retrieval failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/content/draft/<draft_id>", methods=["DELETE"])
def content_delete_draft(draft_id):
    """Delete a draft."""
    try:
        success = content_engine.storage.delete_draft(draft_id)

        if not success:
            return jsonify({"error": f"Draft not found: {draft_id}"}), 404

        logger.info("Draft deleted: %s", draft_id)
        return jsonify({"success": True, "draft_id": draft_id})

    except Exception as error:
        logger.exception("Draft deletion failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/campaign/create", methods=["POST"])
def campaign_create():
    try:
        result = campaign_engine.create_campaign(request.get_json(silent=True) or {})
        if "error" in result:
            return jsonify(result), 400
        logger.info("Campaign draft created: %s", result["id"])
        return jsonify(result), 201
    except Exception as error:
        logger.exception("Campaign creation failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/campaign/history", methods=["GET"])
def campaign_history():
    try:
        return jsonify(campaign_engine.history())
    except Exception as error:
        logger.exception("Campaign history failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/campaign/<campaign_id>", methods=["GET"])
def campaign_detail(campaign_id):
    try:
        campaign = campaign_engine.get(campaign_id)
        if not campaign:
            return jsonify({"error": f"Campaign not found: {campaign_id}"}), 404
        return jsonify(campaign)
    except Exception as error:
        logger.exception("Campaign detail failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/leads/draft-message", methods=["POST"])
def lead_draft_message():
    try:
        result = lead_engine.draft_message(request.get_json(silent=True) or {})
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as error:
        logger.exception("Lead draft failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/leads/save", methods=["POST"])
def lead_save():
    try:
        result = lead_engine.save(request.get_json(silent=True) or {})
        if "error" in result:
            return jsonify(result), 400
        logger.info("Lead draft saved: %s", result["id"])
        return jsonify(result), 201
    except Exception as error:
        logger.exception("Lead save failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/leads/history", methods=["GET"])
def lead_history():
    try:
        return jsonify(lead_engine.history())
    except Exception as error:
        logger.exception("Lead history failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/empire/generate-content", methods=["POST"])
def empire_generate_content():
    return empire_generation_response("platform_content")


@app.route("/api/empire/generate-voiceover", methods=["POST"])
def empire_generate_voiceover():
    return empire_generation_response("voiceover_script")


@app.route("/api/empire/generate-avatar-prompt", methods=["POST"])
def empire_generate_avatar_prompt():
    return empire_generation_response("ai_avatar_prompt")


@app.route("/api/empire/generate-thumbnail-prompt", methods=["POST"])
def empire_generate_thumbnail_prompt():
    return empire_generation_response("thumbnail_prompt")


@app.route("/api/empire/create-posting-queue-item", methods=["POST"])
def empire_create_posting_queue_item():
    try:
        payload = request.get_json(silent=True) or {}
        item = empire_queue.create_item(payload)
        logger.info("Empire queue item created: %s", item["id"])
        return jsonify(item), 201
    except Exception as error:
        logger.exception("Empire queue create failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/empire/posting-queue", methods=["GET"])
def empire_posting_queue():
    try:
        return jsonify(empire_queue.history())
    except Exception as error:
        logger.exception("Empire queue history failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/empire/mark-approved", methods=["POST"])
def empire_mark_approved():
    try:
        payload = request.get_json(silent=True) or {}
        item_id = str(payload.get("id", "")).strip()
        if not item_id:
            return jsonify({"error": "id is required"}), 400
        item = empire_queue.mark_approved(item_id)
        if not item:
            return jsonify({"error": f"Queue item not found: {item_id}"}), 404
        logger.info("Empire queue item approved manually: %s", item_id)
        return jsonify(item)
    except Exception as error:
        logger.exception("Empire queue approval failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/meta/status", methods=["GET"])
def meta_status():
    return jsonify(get_meta_status())


@app.route("/api/meta/test", methods=["POST"])
def meta_test():
    return jsonify(validate_meta_connection())


@app.route("/api/meta/create-facebook-draft", methods=["POST"])
def meta_create_facebook_draft():
    try:
        draft = create_facebook_post_draft(request.get_json(silent=True) or {})
        return jsonify(draft), 201
    except Exception as error:
        logger.exception("Meta Facebook draft failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/meta/create-instagram-draft", methods=["POST"])
def meta_create_instagram_draft():
    try:
        draft = create_instagram_caption_draft(request.get_json(silent=True) or {})
        return jsonify(draft), 201
    except Exception as error:
        logger.exception("Meta Instagram draft failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/meta/queue-post", methods=["POST"])
def meta_queue_post_route():
    try:
        item = queue_meta_post(request.get_json(silent=True) or {})
        logger.info("Meta post queued for manual review: %s", item["id"])
        return jsonify(item), 201
    except Exception as error:
        logger.exception("Meta queue failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/youtube/status", methods=["GET"])
def youtube_status():
    return jsonify(get_youtube_status())


@app.route("/api/platform/full-status", methods=["GET"])
def platform_full_status():
    return jsonify(get_platform_full_status())


@app.route("/api/youtube/oauth-url", methods=["GET"])
def youtube_oauth_url():
    try:
        return jsonify(create_youtube_oauth_url())
    except Exception as error:
        logger.warning("YouTube OAuth URL creation failed: %s", error)
        return jsonify({"error": str(error)}), 400


@app.route("/oauth/callback", methods=["GET"])
def oauth_callback():
    code_present = bool(request.args.get("code"))
    state_present = bool(request.args.get("state"))
    error = request.args.get("error") or ""
    error_description = request.args.get("error_description") or ""
    result = {
        "received_at": datetime.now().isoformat(),
        "code_present": code_present,
        "state_present": state_present,
        "code": request.args.get("code") or "",
        "state": request.args.get("state") or "",
        "error": error,
        "error_description": error_description,
        "query_keys": sorted(request.args.keys()),
        "redirect_uri": request.base_url,
        "token_exchange_performed": False,
    }
    _save_oauth_callback_result(result)

    if error:
        return _oauth_callback_page(False, "OAuth returned an error. Callback metadata was saved."), 400
    if not code_present:
        return _oauth_callback_page(False, "No authorization code was received. Callback metadata was saved."), 400
    return _oauth_callback_page(True, "Authorization code received. Callback metadata was saved."), 200


@app.route("/api/youtube/token-status", methods=["GET"])
def youtube_token_status():
    return jsonify(get_youtube_token_status())


@app.route("/api/youtube/exchange-token", methods=["POST"])
def youtube_exchange_token():
    try:
        status = exchange_youtube_oauth_code()
        _reload_runtime_env()
        return jsonify({**status, "platform_status": get_platform_full_status()})
    except Exception as error:
        logger.warning("YouTube OAuth token exchange failed: %s", error)
        return jsonify({"error": str(error), **get_youtube_token_status()}), 400


@app.route("/api/youtube/create-video-draft", methods=["POST"])
def youtube_create_video_draft():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            logger.warning("YouTube draft validation failed: payload must be an object")
            return jsonify({"error": "payload must be a JSON object"}), 400

        status = get_platform_full_status()["youtube"]
        logger.info(
            "YouTube draft validation: ready=%s missing=%s payload_keys=%s",
            status["ready"],
            status["missing"],
            sorted(payload.keys()),
        )
        if not status["ready"]:
            return jsonify({
                "error": "YouTube setup is not ready",
                "missing": status["missing"],
            }), 400

        draft = create_youtube_video_draft(payload)
        return jsonify(draft), 201
    except Exception as error:
        logger.exception("YouTube video draft failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/youtube/queue-upload-draft", methods=["POST"])
def youtube_queue_upload_draft_route():
    try:
        item = queue_youtube_upload_draft(request.get_json(silent=True) or {})
        logger.info("YouTube upload draft queued for manual review: %s", item["id"])
        return jsonify(item), 201
    except Exception as error:
        logger.exception("YouTube queue failed")
        return jsonify({"error": str(error)}), 500


def _approval_item(source, item):
    return {
        "id": item.get("id") or item.get("draft_id"),
        "source": source,
        "platform": item.get("platform") or ",".join(item.get("platforms", [])) or "manual",
        "content_type": item.get("content_type", source),
        "title": item.get("title", "Untitled"),
        "body": item.get("body") or item.get("content") or item.get("script") or "",
        "status": item.get("status", "draft"),
        "review_status": item.get("review_status", "manual_review"),
        "created_at": item.get("created_at", ""),
        "scheduled_for": item.get("scheduled_for", ""),
    }


@app.route("/api/approval-queue", methods=["GET"])
def approval_queue():
    try:
        items = []

        for draft in content_engine.get_content_history(limit=100).get("drafts", []):
            items.append(_approval_item("content", draft))

        for item in empire_queue.history().get("queue", []):
            items.append(_approval_item("empire", item))

        for item in get_meta_status().get("queue", []):
            items.append(_approval_item("meta", item))

        for item in get_youtube_status().get("queue", []):
            items.append(_approval_item("youtube", item))

        items = sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)

        return jsonify({
            "mode": "manual_review",
            "total": len(items),
            "items": items,
        })
    except Exception as error:
        logger.exception("Approval queue failed")
        return jsonify({"error": str(error)}), 500


def _approval_store(source):
    if source == "content":
        data = content_engine.storage._read_storage()
        return data, "drafts", content_engine.storage._write_storage
    if source == "empire":
        return empire_queue.storage._read(), empire_queue.storage.root_key, empire_queue.storage._write
    if source == "meta":
        return _read_meta_queue(), "queue", _write_meta_queue
    if source == "youtube":
        return _read_youtube_queue(), "queue", _write_youtube_queue
    return None, None, None


def _find_approval_item(source, item_id):
    data, root_key, writer = _approval_store(source)
    if data is None:
        return None, None, None
    for item in data[root_key]:
        if item.get("id") == item_id:
            return item, data, writer
    return None, None, None


def _publish_allowed(item):
    return item.get("status") in ("approved", "scheduled") or item.get("review_status") in ("approved", "scheduled") or bool(item.get("scheduled_for"))


def _mark_publish_success(source, item_id, platform, response):
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return None
    item["status"] = "published"
    item["review_status"] = "published"
    item["published_at"] = datetime.now().isoformat()
    item["publish_platform"] = platform
    item["publish_response"] = response
    item.pop("publish_error", None)
    writer(data)
    return _approval_item(source, item)


def _mark_publish_failure(source, item_id, error):
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return None
    item["publish_error"] = str(error)
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return _approval_item(source, item)


def _publish_request(platform, publisher):
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item, _, _ = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    if not _publish_allowed(item):
        return jsonify({"error": "Only approved or scheduled items can be published"}), 400

    body = payload.get("body") or item.get("body") or item.get("content") or item.get("caption") or item.get("script") or ""
    title = payload.get("title") or item.get("title") or "Orion Publish"
    try:
        response = publisher(item, payload, title, body)
        record = save_publish_result(platform, source, item_id, True, response=response)
        updated = _mark_publish_success(source, item_id, platform, response)
        logger.info("Publish success: platform=%s source=%s id=%s", platform, source, item_id)
        return jsonify({"success": True, "history": record, "item": updated})
    except Exception as error:
        record = save_publish_result(platform, source, item_id, False, error=error)
        updated = _mark_publish_failure(source, item_id, error)
        logger.warning("Publish failed: platform=%s source=%s id=%s error=%s", platform, source, item_id, error.__class__.__name__)
        error_message = str(error) or record.get("error") or "Publish failed"
        return jsonify({"success": False, "history": record, "item": updated, "error": error_message}), 400


def _apply_approval_status(source, item_id, status):
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return None
    item["status"] = status
    item["review_status"] = status
    item["approved"] = status == "approved"
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return _approval_item(source, item)


@app.route("/api/approval-queue/approve", methods=["POST"])
def approval_queue_approve():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item = _apply_approval_status(source, item_id, "approved")
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    return jsonify(item)


@app.route("/api/approval-queue/reject", methods=["POST"])
def approval_queue_reject():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item = _apply_approval_status(source, item_id, "rejected")
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    return jsonify(item)


@app.route("/api/approval-queue/update", methods=["POST"])
def approval_queue_update():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    updates = payload.get("updates") if isinstance(payload.get("updates"), dict) else {}
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404

    allowed_fields = {"title", "body", "caption", "script", "platform", "metadata", "scheduled_for"}
    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        if field == "metadata":
            item[field] = value if isinstance(value, dict) else {}
        else:
            item[field] = str(value)

    if source == "content" and "body" in updates:
        item["content"] = str(updates.get("body", ""))
        item["formatted"] = {
            platform: content_engine.formatter.format_for_platform(item["content"], platform)
            for platform in item.get("platforms", [])
        }

    item["status"] = "draft"
    item["review_status"] = "manual_review"
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return jsonify(_approval_item(source, item))


def _parse_iso_datetime(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
        return text
    except ValueError:
        return None


def _all_approval_items():
    items = []
    for draft in content_engine.get_content_history(limit=100).get("drafts", []):
        items.append(_approval_item("content", draft))
    for item in empire_queue.history().get("queue", []):
        items.append(_approval_item("empire", item))
    for item in get_meta_status().get("queue", []):
        items.append(_approval_item("meta", item))
    for item in get_youtube_status().get("queue", []):
        items.append(_approval_item("youtube", item))
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


@app.route("/api/scheduler/items", methods=["GET"])
def scheduler_items():
    try:
        approved = [item for item in _all_approval_items() if item.get("status") == "approved"]
        scheduled = [item for item in approved if item.get("scheduled_for")]
        unscheduled = [item for item in approved if not item.get("scheduled_for")]
        return jsonify({
            "mode": "manual_scheduler",
            "scheduled": scheduled,
            "unscheduled": unscheduled,
            "total_scheduled": len(scheduled),
            "total_unscheduled": len(unscheduled),
        })
    except Exception as error:
        logger.exception("Scheduler items failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/scheduler/schedule", methods=["POST"])
def scheduler_schedule():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    scheduled_for = _parse_iso_datetime(payload.get("scheduled_for"))
    if not scheduled_for:
        return jsonify({"error": "scheduled_for must be an ISO datetime string"}), 400

    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    if item.get("status") != "approved":
        return jsonify({"error": "Only approved items can be scheduled"}), 400

    item["scheduled_for"] = scheduled_for
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return jsonify(_approval_item(source, item))


@app.route("/api/scheduler/unschedule", methods=["POST"])
def scheduler_unschedule():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    item["scheduled_for"] = ""
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return jsonify(_approval_item(source, item))


@app.route("/api/scheduler/mark-complete", methods=["POST"])
def scheduler_mark_complete():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item, data, writer = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    item["status"] = "completed"
    item["review_status"] = "completed"
    item["updated_at"] = datetime.now().isoformat()
    writer(data)
    return jsonify(_approval_item(source, item))


def _ensure_export_pack_file():
    os.makedirs(os.path.dirname(EXPORT_PACK_PATH), exist_ok=True)
    if not os.path.exists(EXPORT_PACK_PATH):
        with open(EXPORT_PACK_PATH, "w") as f:
            json.dump({"version": "1.0", "packs": []}, f, indent=2)


def _read_export_packs():
    _ensure_export_pack_file()
    try:
        with open(EXPORT_PACK_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", "packs": []}
    data.setdefault("packs", [])
    return data


def _write_export_packs(data):
    _ensure_export_pack_file()
    with open(EXPORT_PACK_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _hashtags(platform, title):
    base = ["#OrionInterface", "#OutlawAI", "#SoundSavageAI"]
    if platform == "youtube":
        return base + ["#YouTubeShorts"]
    if platform in ("tiktok", "instagram"):
        return base + ["#AIContent", "#CreatorTools"]
    return base + ["#LocalAI"]


def _build_export_pack(source, item):
    approval = _approval_item(source, item)
    platform = approval.get("platform") or "manual"
    title = approval.get("title") or "Orion Export"
    body = approval.get("body") or item.get("caption") or item.get("post_text") or ""
    script = item.get("script") or body
    return {
        "id": str(datetime.now().timestamp()).replace(".", ""),
        "created_at": datetime.now().isoformat(),
        "source": source,
        "source_id": approval.get("id"),
        "source_status": approval.get("status"),
        "platform": platform,
        "title": title,
        "caption": body,
        "body": body,
        "hashtags": _hashtags(platform, title),
        "CTA": "Review manually, paste into the platform, and publish only after final human approval.",
        "script": script,
        "thumbnail_prompt": f"Sharp dark tactical thumbnail for {title}, red black steel palette, clear focal subject, high contrast.",
        "voiceover_prompt": f"Confident outlaw AI operator voiceover for {title}. Direct, clean, sales-focused, no hype.",
        "avatar_prompt": f"Professional AI avatar presenter for {title}, Orion command center mood, serious and trustworthy.",
        "posting_notes": "Manual posting only. No automatic upload or platform API call was made.",
        "review_status": "manual_review",
    }


@app.route("/api/export-pack/create", methods=["POST"])
def export_pack_create():
    payload = request.get_json(silent=True) or {}
    source = str(payload.get("source", "")).strip()
    item_id = str(payload.get("id", "")).strip()
    item, _, _ = _find_approval_item(source, item_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404
    if item.get("status") not in ("approved", "completed") and not item.get("scheduled_for"):
        return jsonify({"error": "Only approved or scheduled items can be exported"}), 400

    pack = _build_export_pack(source, item)
    data = _read_export_packs()
    data["packs"].append(pack)
    _write_export_packs(data)
    return jsonify(pack), 201


@app.route("/api/export-pack/history", methods=["GET"])
def export_pack_history():
    data = _read_export_packs()
    packs = sorted(data["packs"], key=lambda pack: pack.get("created_at", ""), reverse=True)
    return jsonify({"total": len(packs), "packs": packs})


@app.route("/api/revenue/create-offer", methods=["POST"])
def revenue_create_offer():
    result = create_offer(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@app.route("/api/revenue/create-lead", methods=["POST"])
def revenue_create_lead():
    result = create_lead(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@app.route("/api/revenue/leads", methods=["GET"])
def revenue_leads():
    return jsonify(get_leads())


@app.route("/api/revenue/update-lead", methods=["POST"])
def revenue_update_lead():
    result = update_lead(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/api/revenue/create-followup", methods=["POST"])
def revenue_create_followup():
    result = create_followup(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@app.route("/api/revenue/followups", methods=["GET"])
def revenue_followups():
    return jsonify(get_followups())


@app.route("/api/revenue/mark-followup-done", methods=["POST"])
def revenue_mark_followup_done():
    result = mark_followup_done(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/api/revenue/report", methods=["GET"])
def revenue_report_route():
    return jsonify(revenue_report())


@app.route("/api/daily/create-task", methods=["POST"])
def daily_create_task():
    result = create_task(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@app.route("/api/daily/tasks", methods=["GET"])
def daily_tasks():
    return jsonify(get_tasks())


@app.route("/api/daily/complete-task", methods=["POST"])
def daily_complete_task():
    result = complete_task(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/api/daily/reset-day", methods=["POST"])
def daily_reset_day():
    return jsonify(reset_day())


@app.route("/api/daily/set-content-goals", methods=["POST"])
def daily_set_content_goals():
    return jsonify(set_content_goals(request.get_json(silent=True) or {}))


@app.route("/api/daily/content-goals", methods=["GET"])
def daily_content_goals():
    return jsonify(get_content_goals())


@app.route("/api/daily/log-revenue", methods=["POST"])
def daily_log_revenue():
    return jsonify(log_revenue(request.get_json(silent=True) or {})), 201


@app.route("/api/daily/revenue-today", methods=["GET"])
def daily_revenue_today():
    return jsonify(revenue_today())


@app.route("/api/platform/youtube/audit-video", methods=["POST"])
def platform_youtube_audit_video():
    return jsonify(audit_video(request.get_json(silent=True) or {})), 201


@app.route("/api/platform/youtube/audit-channel", methods=["POST"])
def platform_youtube_audit_channel():
    return jsonify(audit_channel(request.get_json(silent=True) or {})), 201


@app.route("/api/platform/youtube/fix-draft", methods=["POST"])
def platform_youtube_fix_draft():
    draft = fix_draft(request.get_json(silent=True) or {})
    empire_queue.create_item({"title": draft["update_draft"]["title"], "platform": "youtube", "content_type": "youtube_update_draft", "body": draft["update_draft"]["description"]})
    return jsonify(draft), 201


@app.route("/api/media/create-short-pack", methods=["POST"])
def media_create_short_pack():
    return jsonify(create_short_pack(request.get_json(silent=True) or {})), 201


@app.route("/api/media/create-voiceover-job", methods=["POST"])
def media_create_voiceover_job():
    return jsonify(create_media_job(request.get_json(silent=True) or {}, "voiceover")), 201


@app.route("/api/media/create-avatar-job", methods=["POST"])
def media_create_avatar_job():
    return jsonify(create_media_job(request.get_json(silent=True) or {}, "avatar")), 201


@app.route("/api/media/jobs", methods=["GET"])
def media_jobs():
    return jsonify(get_media_jobs())


@app.route("/api/platform/facebook/create-post-update-draft", methods=["POST"])
def platform_facebook_update_draft():
    draft = platform_update_draft(request.get_json(silent=True) or {}, "facebook")
    empire_queue.create_item({"title": draft["title"], "platform": "facebook", "content_type": draft["content_type"], "body": draft["body"]})
    return jsonify(draft), 201


@app.route("/api/platform/instagram/create-post-update-draft", methods=["POST"])
def platform_instagram_update_draft():
    draft = platform_update_draft(request.get_json(silent=True) or {}, "instagram")
    empire_queue.create_item({"title": draft["title"], "platform": "instagram", "content_type": draft["content_type"], "body": draft["body"]})
    return jsonify(draft), 201


@app.route("/api/platform/comments/create-reply-draft", methods=["POST"])
def platform_comment_reply_draft():
    draft = reply_draft(request.get_json(silent=True) or {})
    empire_queue.create_item({"title": "Comment Reply Draft", "platform": draft["platform"], "content_type": "comment_reply_draft", "body": draft["reply"]})
    return jsonify(draft), 201


@app.route("/api/leads/generate-target-list", methods=["POST"])
def leads_generate_target_list():
    return jsonify(target_list(request.get_json(silent=True) or {})), 201


@app.route("/api/leads/create-outreach-sequence", methods=["POST"])
def leads_create_outreach_sequence():
    return jsonify(outreach_sequence(request.get_json(silent=True) or {})), 201


@app.route("/api/publish/status", methods=["GET"])
def publish_status_route():
    return jsonify(publish_status())


@app.route("/api/publish/history", methods=["GET"])
def publish_history_route():
    return jsonify(publish_history())


@app.route("/api/publish/facebook", methods=["POST"])
def publish_facebook_route():
    return _publish_request(
        "facebook",
        lambda item, payload, title, body: publish_facebook(body),
    )


@app.route("/api/publish/instagram", methods=["POST"])
def publish_instagram_route():
    return _publish_request(
        "instagram",
        lambda item, payload, title, body: publish_instagram(body, payload.get("media_url") or item.get("media_url")),
    )


@app.route("/api/publish/youtube", methods=["POST"])
def publish_youtube_route():
    return _publish_request(
        "youtube",
        lambda item, payload, title, body: publish_youtube(
            title,
            body,
            payload.get("video_path") or item.get("video_path") or item.get("output_path"),
            payload.get("tags") or item.get("tags") or [],
        ),
    )


@app.route("/api/publish/comment-reply", methods=["POST"])
def publish_comment_reply_route():
    return _publish_request(
        "comment_reply",
        lambda item, payload, title, body: publish_comment_reply(payload.get("comment_id") or item.get("comment_id"), body),
    )


if __name__ == "__main__":
    logger.info("Starting Orion application on port %s", APP_PORT)

    app.run(
        host="0.0.0.0",
        port=APP_PORT,
        debug=False
    )

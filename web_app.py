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
    "/api/gpu"
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


if __name__ == "__main__":
    logger.info("Starting Orion application on port %s", APP_PORT)

    app.run(
        host="0.0.0.0",
        port=APP_PORT,
        debug=False
    )
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
import platform
import sys
from datetime import datetime
import psutil

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "online",
        "app": "Orion Interface",
        "ai_ready": True,
        "model": "meta/llama-3.1-8b-instruct",
        "port": 8000,
        "tiktok": "NOT CONFIGURED",
        "voice_route": "registered",
        "memory": {
            "total_conversations": 0,
            "total_facts": 0,
            "memory_file_size": 0
        }
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
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return jsonify({
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

            "runtime": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "boot_time": datetime.fromtimestamp(
                    psutil.boot_time()
                ).isoformat()
            }
        })

    except Exception as error:
        logger.exception("System metrics failed")

        return jsonify({
            "status": "error",
            "error": str(error)
        }), 500

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        return jsonify({
            "response": f"""ORION SYSTEM RESPONSE

Command received:
{message}

Current infrastructure:
- Flask backend online
- NVIDIA/OpenAI configured
- Local AI routing active
- Voice route registered
- System metrics enabled
- Docker prep initialized

Status:
Operational and stable."""
        })

    except Exception as error:
        logger.exception("Chat route failed")

        return jsonify({
            "error": str(error)
        }), 500

if __name__ == "__main__":
    logger.info("Starting Orion application")

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", 8000)),
        debug=False
    )
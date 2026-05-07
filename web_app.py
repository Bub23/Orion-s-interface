import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Force local directory import safety
sys.path.append(os.path.dirname(__file__))

from ai_interface import AIInterface


# -------------------------
# APP SETUP
# -------------------------
app = Flask(
    __name__,
    template_folder="my-local-ai/templates",
    static_folder="my-local-ai/static"
)

# Disable Flask's default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

try:
    ai = AIInterface()
    logger.info("AI Interface initialized successfully")
except Exception as e:
    logger.warning(f"AI Interface failed to initialize: {e}")
    ai = None


# -------------------------
# GLOBAL ERROR HANDLERS
# -------------------------
@app.errorhandler(BadRequest)
def handle_bad_request(e):
    logger.error(f"Bad request: {e}")
    return jsonify({
        "error": "Bad request",
        "message": str(e)
    }), 400


@app.errorhandler(400)
def handle_400(e):
    logger.error(f"400 error: {e}")
    return jsonify({
        "error": "Bad request"
    }), 400


@app.errorhandler(500)
def handle_500(e):
    logger.error(f"500 error: {e}")
    return jsonify({
        "error": "Internal server error"
    }), 500


# -------------------------
# REQUEST LOGGING
# -------------------------
@app.after_request
def log_request(response):
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    return response


# -------------------------
# HOME / DASHBOARD
# -------------------------
@app.route("/")
def home():
    return render_template("chat.html")


# -------------------------
# CHAT ENDPOINT
# -------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        if not ai:
            return jsonify({"error": "AI interface not initialized"}), 503

        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "No message provided"}), 400

        logger.info(f"Chat request: {message[:50]}")
        response = ai.chat(message)

        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -------------------------
# CONTENT GENERATOR
# -------------------------
@app.route("/api/content", methods=["POST"])
def content():
    try:
        if not ai:
            return jsonify({"error": "AI interface not initialized"}), 503

        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"error": "No topic provided"}), 400

        logger.info(f"Content request: {topic}")
        response = ai.generate_content_pack(topic)

        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Content error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -------------------------
# MEMORY SIDEBAR
# -------------------------
@app.route("/api/memories/sidebar", methods=["GET"])
def memory_sidebar():
    try:
        if not ai:
            return jsonify({"error": "AI interface not initialized"}), 503
        return jsonify(ai.get_stats())
    except Exception as e:
        logger.error(f"Memory sidebar error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "ai": "connected" if ai else "not initialized"
    })


# -------------------------
# RUN SERVER (development only)
# -------------------------
if __name__ == "__main__":
    logger.info("Starting Orion application")
    app.run(
        debug=False,
        host="0.0.0.0",
        port=8000
    )

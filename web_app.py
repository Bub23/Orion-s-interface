import os
import sys
from flask import Flask, render_template, request, jsonify

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

ai = AIInterface()


# -------------------------
# HOME / DASHBOARD
# -------------------------
@app.route("/")
def home():
    return render_template("chat.html")


# -------------------------
# CHAT ENDPOINT (MAIN AI PIPE)
# -------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        response = ai.chat(message)

        return jsonify({
            "response": response
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# -------------------------
# CONTENT GENERATOR
# -------------------------
@app.route("/api/content", methods=["POST"])
def content():
    try:
        data = request.json or {}
        topic = data.get("topic", "")

        if not topic:
            return jsonify({"error": "No topic provided"}), 400

        response = ai.generate_content_pack(topic)

        return jsonify({
            "response": response
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# -------------------------
# MEMORY SIDEBAR
# -------------------------
@app.route("/api/memories/sidebar", methods=["GET"])
def memory_sidebar():
    try:
        return jsonify(ai.get_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "ai": "connected"
    })


# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    print("🔥 Orion Browser Stable Running")
    print("👉 http://127.0.0.1:5000")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
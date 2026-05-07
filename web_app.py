import os
import sys
from flask import Flask, render_template, request, jsonify
import traceback

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

try:
    ai = AIInterface()
except Exception as e:
    print(f"Warning: AI Interface failed to initialize: {e}")
    ai = None


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
        if not ai:
            return jsonify({"error": "AI interface not initialized"}), 503

        try:
            data = request.get_json(silent=True) or {}
        except Exception as e:
            print(f"JSON parse error: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Failed to parse JSON: {str(e)}"}), 400

        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "No message provided"}), 400

        response = ai.chat(message)

        return jsonify({
            "response": response
        })

    except Exception as e:
        print(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


# -------------------------
# CONTENT GENERATOR
# -------------------------
@app.route("/api/content", methods=["POST"])
def content():
    try:
        if not ai:
            return jsonify({"error": "AI interface not initialized"}), 503

        try:
            data = request.get_json(silent=True) or {}
        except Exception as e:
            print(f"JSON parse error: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Failed to parse JSON: {str(e)}"}), 400

        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"error": "No topic provided"}), 400

        response = ai.generate_content_pack(topic)

        return jsonify({
            "response": response
        })

    except Exception as e:
        print(f"Content error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


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
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    print("🔥 Orion Browser Stable Running")
    print("👉 http://0.0.0.0:8000")

    app.run(
        debug=False,
        host="0.0.0.0",
        port=8000
    )

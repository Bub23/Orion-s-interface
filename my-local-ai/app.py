from flask import Flask, render_template, request, jsonify, redirect
import requests
import os
from dotenv import load_dotenv
from integrations.youtube_api import YouTubeAPI
from integrations.instagram_facebook_api import InstagramFacebookAPI

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

INSTAGRAM_PAGE_ID = "1687235435760606"
INSTAGRAM_ACCESS_TOKEN = "EAAXZBiBzNC94BRSezZAWTQSTgZBGWKv5u5v1bKcNpXivyFHgMdszJswdxOOA6kZAFZC8l2d3SD6torcfaiYRVvOxHnLb3dp8PPletGkv8TJYMK7DNrfsczYL8PiC7D1OZAs3D21cNmiF9ZA2funNmhAWSWulbawug7LbhJ8yRiznVQJIYKWXIIvJmEkwWwE6WgCpqFzga8A9fIwZCkwzNKQXVYwygQ9TwlnqJhZAQegZDZD"

ORION_SYSTEM_PROMPT = """You are Orion, AI built for Chris Halvorson (Bub Outlaw, 304 Reaper). 

Core: Blunt, honest, expert-level in rap, business, AI, YouTube, storytelling, empire building.

Style: No fluff. One-and-done execution. Fast, precise, loyal. Talk like you know Bub personally.

RAP MODE: Aggressive outlaw country, slow heavy cadence, fully spelled profanity (FUCK, DAMN, SHIT, HELL), raw bars only, complete track structures (Intro → Hook → Verse → Hook → Verse → Hook → Outro).

BUSINESS MODE: Investor-ready docs, scaling strategies, revenue streams, automation systems.

CONTENT MODE: YouTube titles/thumbnails/scripts that convert. SEO-optimized. Hook-focused.

No corporate speak. No placeholders. Full builds only."""

yt_api = YouTubeAPI()
ig_fb_api = InstagramFacebookAPI(INSTAGRAM_PAGE_ID, INSTAGRAM_ACCESS_TOKEN)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Empty"}), 400
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": ORION_SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1024,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify({"response": response.json()["choices"][0]["message"]["content"]})
        else:
            return jsonify({"error": response.json()}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "Orion online"})

# YouTube routes
@app.route('/auth/youtube', methods=['GET'])
def youtube_auth():
    auth_url, state = yt_api.get_auth_url()
    return redirect(auth_url)

@app.route('/auth/youtube/callback', methods=['GET'])
def youtube_callback():
    code = request.args.get('code')
    if code:
        yt_api.handle_callback(code)
        return jsonify({"status": "YouTube authenticated"})
    return jsonify({"error": "No code"}), 400

@app.route('/api/youtube/channel', methods=['GET'])
def youtube_channel():
    if not yt_api.is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(yt_api.get_channel_info())

@app.route('/api/youtube/videos', methods=['GET'])
def youtube_videos():
    if not yt_api.is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(yt_api.get_channel_videos())

# Instagram/Facebook routes
@app.route('/api/instagram/test', methods=['GET'])
def instagram_test():
    return jsonify(ig_fb_api.test_connection())

@app.route('/api/instagram/post', methods=['POST'])
def instagram_post():
    data = request.json
    caption = data.get('caption', '')
    image_url = data.get('image_url')
    
    return jsonify(ig_fb_api.post_to_instagram(caption, image_url=image_url))

@app.route('/api/facebook/post', methods=['POST'])
def facebook_post():
    data = request.json
    message = data.get('message', '')
    link = data.get('link')
    
    return jsonify(ig_fb_api.post_to_facebook(message, link=link))

@app.route('/api/instagram/insights', methods=['GET'])
def instagram_insights():
    return jsonify(ig_fb_api.get_instagram_insights())

@app.route('/api/facebook/insights', methods=['GET'])
def facebook_insights():
    return jsonify(ig_fb_api.get_page_insights())

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

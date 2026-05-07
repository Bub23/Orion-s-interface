from flask import Flask, request, jsonify, render_template, session
import os
from functools import wraps
from engine.content_engine import ContentEngine
from engine.hook_generator import HookGenerator
from engine.distributor import MultiPlatformDistributor
from engine.performance_tracker import PerformanceTracker

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Initialize engines
ce = ContentEngine()
hg = HookGenerator()
mpd = MultiPlatformDistributor()
pt = PerformanceTracker()

# Auth middleware
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ─────────────────────────────────────────
# CONTENT ENGINE ROUTES
# ─────────────────────────────────────────

@app.route("/api/content/submit-idea", methods=["POST"])
@require_auth
def submit_idea():
    """Submit manual content idea"""
    data = request.json
    
    result = ce.submit_manual_idea(
        user_id=session["user_id"],
        content_type=data.get("type", "idea"),
        input_text=data.get("text")
    )
    
    return jsonify(result)

@app.route("/api/content/daily-prompts", methods=["GET"])
@require_auth
def get_daily_prompts():
    """Get 10 daily trending prompts + weighted queue"""
    niche = request.args.get("niche", "ai tools")
    
    # Generate trend prompts
    prompts = ce.generate_trend_prompts(
        user_id=session["user_id"],
        niche=niche
    )
    
    # Get full queue (40/40/20 weighted)
    queue = ce.get_daily_content_queue(session["user_id"])
    
    return jsonify({
        "trending_prompts": prompts,
        "queue": queue
    })

@app.route("/api/content/queue", methods=["GET"])
@require_auth
def get_content_queue():
    """Get weighted content queue (40% manual, 40% trend, 20% remix)"""
    queue = ce.get_daily_content_queue(session["user_id"])
    return jsonify(queue)

@app.route("/api/content/remix", methods=["POST"])
@require_auth
def remix_content():
    """Remix high-performing content into new angles"""
    data = request.json
    
    result = ce.remix_content(
        user_id=session["user_id"],
        original_content_id=data.get("content_id"),
        remix_type=data.get("type", "variation")  # variation, sequel, angle_flip, part_2
    )
    
    return jsonify(result)

# ─────────────────────────────────────────
# HOOK GENERATOR ROUTES
# ─────────────────────────────────────────

@app.route("/api/hooks/generate", methods=["POST"])
@require_auth
def generate_hooks():
    """Generate 5 viral hooks from content"""
    data = request.json
    
    result = hg.generate_hooks_from_content(
        content_id=data.get("content_id"),
        content_text=data.get("text"),
        num_hooks=5
    )
    
    return jsonify(result)

@app.route("/api/hooks/rank/<int:content_id>", methods=["GET"])
@require_auth
def rank_hooks(content_id):
    """Rank hooks by performance for a piece of content"""
    hooks = hg.rank_hooks_by_performance(content_id)
    return jsonify({"hooks": hooks})

@app.route("/api/hooks/mark-performer", methods=["POST"])
@require_auth
def mark_hook_performer():
    """Mark a hook as high performer (triggers learning loop)"""
    data = request.json
    
    result = hg.mark_hook_high_performer(data.get("hook_id"))
    return jsonify(result)

@app.route("/api/hooks/variations", methods=["POST"])
@require_auth
def generate_variations():
    """ACTION 1: Auto-generate 5 variations of high-performing hook"""
    data = request.json
    
    result = hg.auto_generate_hook_variations(
        hook_id=data.get("hook_id"),
        num_variations=5
    )
    
    return jsonify(result)

# ─────────────────────────────────────────
# DISTRIBUTOR ROUTES (THE ONE-CLICK DROP)
# ─────────────────────────────────────────

@app.route("/api/drop", methods=["POST"])
@require_auth
def drop_button():
    """ONE-CLICK DROP — Publish everywhere in under 60 seconds"""
    data = request.json
    
    result = mpd.drop_button(
        user_id=session["user_id"],
        video_id=data.get("video_id"),
        platform_targets=data.get("platforms", None)
    )
    
    return jsonify(result)

@app.route("/api/drop/status/<int:video_id>", methods=["GET"])
@require_auth
def check_drop_status(video_id):
    """Check DROP status across all platforms"""
    result = mpd.get_drop_status(video_id)
    return jsonify(result)

@app.route("/api/drop/bulk", methods=["POST"])
@require_auth
def bulk_drop_queue():
    """Queue up multiple videos for staggered drops"""
    data = request.json
    
    result = mpd.bulk_drop_queue(
        user_id=session["user_id"],
        num_videos=data.get("num_videos", 5)
    )
    
    return jsonify(result)

# ─────────────────────────────────────────
# PERFORMANCE TRACKER ROUTES (DASHBOARD)
# ─────────────────────────────────────────

@app.route("/api/dashboard/stats", methods=["GET"])
@require_auth
def dashboard_stats():
    """War room — live dashboard metrics"""
    stats = pt.get_live_dashboard_stats(session["user_id"])
    return jsonify(stats)

@app.route("/api/dashboard/platforms", methods=["GET"])
@require_auth
def platform_comparison():
    """Which platform is winning?"""
    result = pt.get_platform_comparison(session["user_id"])
    return jsonify(result)

@app.route("/api/dashboard/patterns", methods=["GET"])
@require_auth
def hook_patterns():
    """Which hook patterns are winning?"""
    result = pt.get_hook_pattern_learning()
    return jsonify(result)

@app.route("/api/dashboard/weekly-trend", methods=["GET"])
@require_auth
def weekly_trend():
    """7-day performance trend"""
    result = pt.get_weekly_trend(session["user_id"], days=7)
    return jsonify(result)

@app.route("/api/metrics/track", methods=["POST"])
@require_auth
def track_metrics():
    """Log real metrics from a post (called by platform integrations)"""
    data = request.json
    
    result = pt.track_post_metrics(
        post_id=data.get("post_id"),
        views=data.get("views", 0),
        engagement=data.get("engagement", 0),
        clicks=data.get("clicks", 0),
        shares=data.get("shares", 0),
        comments=data.get("comments", 0)
    )
    
    return jsonify(result)

# ─────────────────────────────────────────
# MEMBERSHIP TIERS ROUTES
# ─────────────────────────────────────────

@app.route("/api/subscriptions/tiers", methods=["GET"])
def get_tiers():
    """Get all subscription tiers"""
    tiers = {
        "free": {
            "name": "Free",
            "features": [
                "5 daily content prompts",
                "Basic hook generator",
                "Manual content only"
            ],
            "price": 0
        },
        "creator_pack": {
            "name": "Creator Pack",
            "features": [
                "Unlimited daily prompts",
                "Hook generator + variations",
                "Basic ghostwriter",
                "Beat tools access"
            ],
            "price": 29
        },
        "music_pack": {
            "name": "Music Pack",
            "features": [
                "Everything in Creator Pack",
                "Full song builder",
                "Reaper Flow coach",
                "AI vocals + tools"
            ],
            "price": 79
        },
        "empire_pass": {
            "name": "Empire Pass",
            "features": [
                "Everything unlocked",
                "Vault access",
                "Early drops + exclusives",
                "Priority support",
                "Custom integrations"
            ],
            "price": 199
        }
    }
    
    return jsonify(tiers)

@app.route("/api/user/subscription", methods=["GET"])
@require_auth
def get_user_subscription():
    """Get user's current subscription tier"""
    import sqlite3
    conn = sqlite3.connect("database/orion.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT tier FROM subscriptions WHERE user_id = ?", (session["user_id"],))
    sub = cursor.fetchone()
    conn.close()
    
    tier = sub[0] if sub else "free"
    
    return jsonify({"tier": tier, "user_id": session["user_id"]})

@app.route("/api/subscriptions/upgrade", methods=["POST"])
@require_auth
def upgrade_subscription():
    """Upgrade subscription (payment wired later)"""
    data = request.json
    
    import sqlite3
    conn = sqlite3.connect("database/orion.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subscriptions SET tier = ?
        WHERE user_id = ?
    """, (data.get("tier"), session["user_id"]))
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "upgraded", "tier": data.get("tier")})

# ─────────────────────────────────────────
# DASHBOARD UI ROUTE
# ─────────────────────────────────────────

@app.route("/dashboard")
@require_auth
def dashboard():
    """Main war room dashboard"""
    return render_template("dashboard.html")

@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)


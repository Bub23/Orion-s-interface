import sqlite3
from datetime import datetime
import json
import os

DB_PATH = "database/orion.db"

class ContentEngine:
    """Core engine: takes idea → generates hooks → creates videos → publishes everywhere"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ─────────────────────────────────────────
    # LAYER A: MANUAL INPUT
    # ─────────────────────────────────────────
    def submit_manual_idea(self, user_id, content_type, input_text):
        """
        User submits idea directly
        content_type: "story", "idea", "rant", "concept"
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO content (user_id, content_type, input_text, source)
            VALUES (?, ?, ?, ?)
        """, (user_id, content_type, input_text, "manual"))
        
        conn.commit()
        content_id = cursor.lastrowid
        conn.close()
        
        return {"content_id": content_id, "source": "manual", "status": "queued"}
    
    # ─────────────────────────────────────────
    # LAYER B: TREND MINER (AUTOMATED)
    # ─────────────────────────────────────────
    def generate_trend_prompts(self, user_id, niche="ai tools"):
        """
        Generate 10 daily content prompts from trends
        Returns prompts ranked by viral probability
        """
        # Simulated trending topics (in production, scrape TikTok/YouTube APIs)
        trends = {
            "ai tools": [
                "AI just replaced 3 jobs in 10 seconds",
                "This AI model costs $0.01 per 1M tokens",
                "ChatGPT alternative that's actually better",
                "I tested 5 AI video generators - here's the winner",
                "This AI finds trending content before it blows up",
            ],
            "country rap": [
                "Country rap beats that actually slap",
                "From Nashville to SoundCloud - the rise of trap twang",
                "Mixing banjos with 808s changed everything",
                "Why country rappers are outselling trap artists",
                "Raw Southern bars over trap production",
            ],
            "hustle": [
                "I made $10K in 24 hours - here's how",
                "The hustle economy is killing your 9-5",
                "Side gigs that actually pay",
                "Building passive income from zero",
                "Scaling to 6 figures in 6 months",
            ]
        }
        
        selected_trends = trends.get(niche, trends["ai tools"])[:10]
        
        prompts = []
        for idx, trend in enumerate(selected_trends):
            prompt = {
                "id": idx + 1,
                "text": trend,
                "viral_probability": 0.7 - (idx * 0.05),  # Ranked by probability
                "niche": niche
            }
            prompts.append(prompt)
            
            # Store in database
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content (user_id, content_type, input_text, source, viral_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, "trend", trend, "trend_miner", prompt["viral_probability"]))
            conn.commit()
            conn.close()
        
        return prompts
    
    # ─────────────────────────────────────────
    # LAYER C: REMIX ENGINE
    # ─────────────────────────────────────────
    def remix_content(self, user_id, original_content_id, remix_type="variation"):
        """
        Remix_type: "variation", "sequel", "angle_flip", "part_2"
        Takes existing high-performer and creates new angles
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get original content
        cursor.execute("SELECT input_text FROM content WHERE id = ?", (original_content_id,))
        original = cursor.fetchone()
        
        if not original:
            return {"error": "Content not found"}
        
        remix_variations = {
            "variation": f"[Different angle] {original['input_text']}",
            "sequel": f"Part 2: The truth about {original['input_text']}",
            "angle_flip": f"Why everyone's wrong about {original['input_text']}",
            "part_2": f"Update: What happened after {original['input_text']}"
        }
        
        remix_text = remix_variations.get(remix_type, remix_variations["variation"])
        
        cursor.execute("""
            INSERT INTO content (user_id, content_type, input_text, source)
            VALUES (?, ?, ?, ?)
        """, (user_id, f"remix_{remix_type}", remix_text, "remix_engine"))
        
        remix_id = cursor.lastrowid
        
        # Track remix relationship
        cursor.execute("""
            INSERT INTO remixes (original_content_id, remix_content_id, remix_type)
            VALUES (?, ?, ?)
        """, (original_content_id, remix_id, remix_type))
        
        conn.commit()
        conn.close()
        
        return {
            "remix_id": remix_id,
            "remix_type": remix_type,
            "text": remix_text,
            "status": "queued"
        }
    
    # ─────────────────────────────────────────
    # HYBRID WEIGHTING (40/40/20)
    # ─────────────────────────────────────────
    def get_daily_content_queue(self, user_id):
        """
        Returns daily queue weighted 40% manual + 40% trend + 20% remix
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get manual content (40%)
        cursor.execute("""
            SELECT * FROM content WHERE user_id = ? AND source = 'manual'
            ORDER BY created_at DESC LIMIT 2
        """, (user_id,))
        manual = cursor.fetchall()
        
        # Get trend content (40%)
        cursor.execute("""
            SELECT * FROM content WHERE user_id = ? AND source = 'trend_miner'
            ORDER BY viral_score DESC LIMIT 2
        """, (user_id,))
        trends = cursor.fetchall()
        
        # Get remix content (20%)
        cursor.execute("""
            SELECT * FROM content WHERE user_id = ? AND source LIKE 'remix_%'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        remixes = cursor.fetchall()
        
        conn.close()
        
        queue = {
            "manual": [dict(row) for row in manual],
            "trends": [dict(row) for row in trends],
            "remixes": [dict(row) for row in remixes],
            "total_queued": len(manual) + len(trends) + len(remixes)
        }
        
        return queue


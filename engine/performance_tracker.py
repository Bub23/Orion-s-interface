import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "database/orion.db"

class PerformanceTracker:
    """Real-time metrics + auto-learning loop"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def track_post_metrics(self, post_id, views=0, engagement=0, clicks=0, shares=0, comments=0):
        """
        Log real metrics from a post
        In production, pull from platform APIs every 6 hours
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Calculate derived metrics
        retention_rate = (engagement / max(views, 1)) * 100 if views > 0 else 0
        ctr = (clicks / max(views, 1)) * 100 if views > 0 else 0
        
        # Viral score formula: (shares + comments) / views * 1000
        viral_score = ((shares + comments) / max(views, 1)) * 1000 if views > 0 else 0
        
        cursor.execute("""
            INSERT INTO performance (post_id, views, engagement, clicks, shares, comments, retention_rate, ctr, viral_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (post_id, views, engagement, clicks, shares, comments, retention_rate, ctr, viral_score))
        
        conn.commit()
        
        # Get post details
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
        # Get video + hook details
        cursor.execute("SELECT * FROM videos WHERE id = ?", (post["video_id"],))
        video = cursor.fetchone()
        
        cursor.execute("SELECT * FROM hooks WHERE id = ?", (video["hook_id"],))
        hook = cursor.fetchone()
        
        conn.close()
        
        result = {
            "post_id": post_id,
            "platform": post["platform"],
            "viral_score": viral_score,
            "retention_rate": f"{retention_rate:.1f}%",
            "ctr": f"{ctr:.1f}%",
            "hooks_id": hook["id"] if hook else None
        }
        
        # TRIGGER LEARNING LOOP if viral_score > threshold
        if viral_score > 5:  # Threshold for "high performer"
            self._trigger_learning_loop(hook["id"] if hook else None)
        
        return result
    
    def _trigger_learning_loop(self, hook_id):
        """
        When a post goes viral, trigger the 3 automatic actions:
        1. Auto-remix (generate variations)
        2. Auto-reuse (inject into next 5 prompts)
        3. Auto-tag (mark pattern for AI learning)
        """
        from hook_generator import HookGenerator
        from content_engine import ContentEngine
        
        hg = HookGenerator()
        ce = ContentEngine()
        
        if hook_id:
            # ACTION 1: Auto-remix
            variations = hg.auto_generate_hook_variations(hook_id, num_variations=5)
            
            # ACTION 3: Auto-tag (mark as high performer)
            hg.mark_hook_high_performer(hook_id)
        
        return {"learning_triggered": True}
    
    def get_live_dashboard_stats(self, user_id):
        """
        War room dashboard — live metrics across all posts
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get all posts for user
        cursor.execute("""
            SELECT p.*, perf.viral_score, perf.views, perf.retention_rate
            FROM posts p
            JOIN videos v ON p.video_id = v.id
            JOIN content c ON v.content_id = c.id
            JOIN performance perf ON p.id = perf.post_id
            WHERE c.user_id = ?
            ORDER BY perf.viral_score DESC
        """, (user_id,))
        
        posts = cursor.fetchall()
        
        # Categorize by performance
        viral = []      # 🔴 High performers
        mid = []        # 🟡 Mid performers
        dead = []       # ⚫ Low performers
        
        for post in posts:
            post_dict = dict(post)
            if post_dict["viral_score"] > 10:
                viral.append(post_dict)
            elif post_dict["viral_score"] > 2:
                mid.append(post_dict)
            else:
                dead.append(post_dict)
        
        # Overall stats
        cursor.execute("""
            SELECT
            SUM(perf.views) as total_views,
            AVG(perf.viral_score) as avg_viral_score,
            COUNT(DISTINCT p.id) as total_posts
            FROM posts p
            JOIN performance perf ON p.id = perf.post_id
            JOIN videos v ON p.video_id = v.id
            JOIN content c ON v.content_id = c.id
            WHERE c.user_id = ?
        """, (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            "user_id": user_id,
            "overall": {
                "total_views": stats["total_views"] or 0,
                "avg_viral_score": round(stats["avg_viral_score"] or 0, 2),
                "total_posts": stats["total_posts"] or 0
            },
            "performance_breakdown": {
                "🔴_viral_hot": len(viral),
                "🟡_mid_performers": len(mid),
                "⚫_dead_content": len(dead)
            },
            "top_viral_posts": viral[:5],
            "mid_performers": mid[:5]
        }
    
    def get_platform_comparison(self, user_id):
        """
        Which platform is winning?
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
            p.platform,
            COUNT(p.id) as post_count,
            AVG(perf.viral_score) as avg_viral,
            SUM(perf.views) as total_views
            FROM posts p
            JOIN performance perf ON p.id = perf.post_id
            JOIN videos v ON p.video_id = v.id
            JOIN content c ON v.content_id = c.id
            WHERE c.user_id = ?
            GROUP BY p.platform
            ORDER BY total_views DESC
        """, (user_id,))
        
        platforms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "user_id": user_id,
            "platform_stats": platforms
        }
    
    def get_hook_pattern_learning(self):
        """
        Which hook patterns are winning?
        AI uses this to improve future generations
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
            hook_type,
            COUNT(*) as times_tested,
            SUM(CASE WHEN performance_score > 5 THEN 1 ELSE 0 END) as times_succeeded,
            AVG(performance_score) as avg_performance,
            ROUND(100.0 * SUM(CASE WHEN performance_score > 5 THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
            FROM hooks
            GROUP BY hook_type
            ORDER BY success_rate DESC
        """)
        
        patterns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "top_performing_patterns": patterns[:5],
            "learning": "AI will prioritize these patterns for future generation"
        }
    
    def get_weekly_trend(self, user_id, days=7):
        """
        7-day performance trend
        Used to detect rising/falling content
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT
            DATE(p.published_at) as day,
            COUNT(p.id) as posts,
            AVG(perf.viral_score) as avg_viral,
            SUM(perf.views) as views
            FROM posts p
            LEFT JOIN performance perf ON p.id = perf.post_id
            JOIN videos v ON p.video_id = v.id
            JOIN content c ON v.content_id = c.id
            WHERE c.user_id = ? AND p.published_at >= ?
            GROUP BY DATE(p.published_at)
            ORDER BY day DESC
        """, (user_id, start_date))
        
        daily_data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "daily_breakdown": daily_data
        }


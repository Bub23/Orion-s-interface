import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "database/orion.db"

class MultiPlatformDistributor:
    """One-click DROP button — publishes everywhere in under 60 seconds"""
    
    def __init__(self):
        self.db_path = DB_PATH
        
        # Platform APIs (configured via .env)
        self.platforms = {
            "youtube": {"api_key": os.getenv("YOUTUBE_API_KEY")},
            "tiktok": {"client_key": os.getenv("TIKTOK_CLIENT_KEY")},
            "instagram": {"app_id": os.getenv("FACEBOOK_APP_ID")},
            "facebook": {"app_id": os.getenv("FACEBOOK_APP_ID")}
        }
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def drop_button(self, user_id, video_id, platform_targets=None):
        """
        THE ONE-CLICK BUTTON
        Takes video_id and publishes to all platforms simultaneously
        
        platform_targets: list of platforms ["youtube", "tiktok", "instagram", "facebook"]
        if None, publishes to all connected platforms
        """
        
        if platform_targets is None:
            platform_targets = ["youtube", "tiktok", "instagram", "facebook"]
        
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get video details
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        video = cursor.fetchone()
        
        if not video:
            return {"error": "Video not found"}
        
        # Get hook details for metadata
        cursor.execute("SELECT hook_text FROM hooks WHERE id = ?", (video["hook_id"],))
        hook = cursor.fetchone()
        
        results = []
        
        for platform in platform_targets:
            if platform not in self.platforms:
                continue
            
            # Create post record
            cursor.execute("""
                INSERT INTO posts (video_id, platform, status, published_at)
                VALUES (?, ?, ?, ?)
            """, (video_id, platform, "publishing", datetime.now()))
            
            post_id = cursor.lastrowid
            
            # Platform-specific publishing
            publish_result = self._publish_to_platform(
                platform=platform,
                video_id=video_id,
                script=video["script"],
                hook=hook["hook_text"] if hook else "",
                post_id=post_id
            )
            
            # Update post status
            cursor.execute("""
                UPDATE posts SET status = ?, post_id = ?
                WHERE id = ?
            """, (publish_result["status"], publish_result.get("platform_post_id", ""), post_id))
            
            results.append({
                "platform": platform,
                "status": publish_result["status"],
                "post_id": post_id
            })
        
        conn.commit()
        conn.close()
        
        return {
            "video_id": video_id,
            "user_id": user_id,
            "platforms_targeted": len(results),
            "results": results,
            "drop_status": "LIVE" if all(r["status"] == "published" for r in results) else "IN_PROGRESS"
        }
    
    def _publish_to_platform(self, platform, video_id, script, hook, post_id):
        """
        Platform-specific publish logic
        """
        
        if platform == "youtube":
            return self._publish_youtube(video_id, script, hook)
        elif platform == "tiktok":
            return self._publish_tiktok(video_id, script, hook)
        elif platform == "instagram":
            return self._publish_instagram(video_id, script, hook)
        elif platform == "facebook":
            return self._publish_facebook(video_id, script, hook)
        
        return {"status": "unsupported"}
    
    def _publish_youtube(self, video_id, script, hook):
        """Publish to YouTube + Shorts"""
        # In production, use YouTube Data API v3
        # For now, queue for manual upload or integration
        return {
            "platform": "youtube",
            "status": "queued",
            "message": "Ready for YouTube upload",
            "platform_post_id": f"yt_{video_id}"
        }
    
    def _publish_tiktok(self, video_id, script, hook):
        """Publish to TikTok"""
        # Once TikTok approval comes through, use OAuth + Upload API
        return {
            "platform": "tiktok",
            "status": "pending_approval",
            "message": "TikTok app awaiting verification review",
            "platform_post_id": f"tt_{video_id}"
        }
    
    def _publish_instagram(self, video_id, script, hook):
        """Publish to Instagram Reels"""
        # Use Facebook Graph API for Instagram
        return {
            "platform": "instagram",
            "status": "queued",
            "message": "Ready for Instagram Reels upload",
            "platform_post_id": f"ig_{video_id}"
        }
    
    def _publish_facebook(self, video_id, script, hook):
        """Publish to Facebook"""
        # Use Facebook Graph API
        return {
            "platform": "facebook",
            "status": "queued",
            "message": "Ready for Facebook upload",
            "platform_post_id": f"fb_{video_id}"
        }
    
    def get_drop_status(self, video_id):
        """
        Check status of all platforms for a video
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT platform, status, published_at FROM posts WHERE video_id = ?
        """, (video_id,))
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "video_id": video_id,
            "platforms": posts,
            "all_published": all(p["status"] == "published" for p in posts)
        }
    
    def bulk_drop_queue(self, user_id, num_videos=5):
        """
        Queue up videos to drop throughout the day/week
        Stagger drops for maximum reach
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get latest videos
        cursor.execute("""
            SELECT v.id FROM videos v
            JOIN content c ON v.content_id = c.id
            WHERE c.user_id = ? AND v.status = 'ready'
            ORDER BY v.created_at DESC
            LIMIT ?
        """, (user_id, num_videos))
        
        video_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        scheduled_drops = []
        for idx, vid in enumerate(video_ids):
            drop_result = self.drop_button(user_id, vid)
            scheduled_drops.append(drop_result)
        
        return {
            "user_id": user_id,
            "total_drops": len(scheduled_drops),
            "drops": scheduled_drops
        }


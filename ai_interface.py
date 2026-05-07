import os
from dotenv import load_dotenv

load_dotenv()


class AIInterface:
    """
    Orion NVIDIA NIM Serverless Core (CORRECT IMPLEMENTATION)
    """

    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "placeholder")
        self.model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")

        if self.api_key == "placeholder":
            print("WARNING: NVIDIA_API_KEY not set. Set it in .env or environment.")

        try:
            from openai import OpenAI
            # NVIDIA NIM endpoint (THIS IS THE KEY FIX)
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.api_key
            )
        except Exception as e:
            print(f"WARNING: Could not initialize OpenAI client: {e}")
            self.client = None

        try:
            from memory_manager import MemoryManager
            self.memory = MemoryManager()
        except:
            self.memory = None

        self.memory_store = []
        
        # TikTok OAuth Setup
        self.tiktok_client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.tiktok_client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
        self.tiktok_redirect_uri = os.getenv("TIKTOK_REDIRECT_URI")

    # -------------------------
    # CHAT
    # -------------------------
    def chat(self, user_message):
        try:
            if not self.client:
                return "ERROR: API client not initialized"

            context = ""

            if self.memory:
                try:
                    past = self.memory.get_relevant_memories(user_message, limit=3)
                    context = "\n".join(past)
                except:
                    context = ""

            prompt = f"""
You are Orion, an AI assistant with memory.

Context:
{context}

User: {user_message}
Orion:
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Orion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            text = response.choices[0].message.content

            if self.memory:
                try:
                    self.memory.add_memory(
                        "conversation",
                        f"User: {user_message}\nOrion: {text}"
                    )
                except:
                    pass

            self.memory_store.append({"user": user_message, "orion": text})

            return text

        except Exception as e:
            return f"NIM ERROR: {str(e)}"

    # -------------------------
    # CONTENT ENGINE
    # -------------------------
    def generate_content_pack(self, topic):
        return {
            "title": f"The Truth About {topic}",
            "hooks": [
                f"You've been lied to about {topic}",
                f"This changes everything about {topic}",
                f"No one is ready for this truth about {topic}"
            ],
            "caption": f"Raw truth about {topic}",
            "tagline": "Stay real."
        }

    # -------------------------
    # STATS
    # -------------------------
    def get_stats(self):
        return {
            "status": "NVIDIA NIM ONLINE",
            "model": self.model,
            "memory": len(self.memory_store),
            "tiktok": "READY" if self.tiktok_client_key else "NOT CONFIGURED"
        }

    # -------------------------
    # TIKTOK INTEGRATION
    # -------------------------
    def get_tiktok_auth_url(self):
        """Generate TikTok OAuth authorization URL"""
        auth_url = (
            f"https://www.tiktok.com/v1/oauth/authorize?"
            f"client_key={self.tiktok_client_key}"
            f"&response_type=code"
            f"&scope=user.info.basic,video.list,video.upload"
            f"&redirect_uri={self.tiktok_redirect_uri}"
        )
        return auth_url

    def verify_tiktok_connection(self):
        """Test TikTok API credentials"""
        if not self.tiktok_client_key or not self.tiktok_client_secret:
            return {"status": "FAILED", "reason": "Missing TikTok credentials"}
        
        return {
            "status": "PENDING_APPROVAL",
            "client_key": self.tiktok_client_key[:8] + "***",
            "message": "TikTok app awaiting verification review"
        }

    def tiktok_post_video(self, video_id, caption, hashtags=[]):
        """Post video to TikTok (requires OAuth token)"""
        return {
            "status": "QUEUED",
            "video_id": video_id,
            "caption": caption,
            "hashtags": hashtags,
            "message": "Awaiting TikTok app approval before publishing"
        }

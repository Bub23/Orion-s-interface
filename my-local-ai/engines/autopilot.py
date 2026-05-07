import time
import random
import requests

class AutopilotEngine:

    def __init__(self, n8n_url):
        self.n8n_url = n8n_url
        self.active = True

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def run(self, agi, growth, video_pipeline):
        """
        Fully autonomous content loop.
        """

        while self.active:

            # 1. GENERATE IDEA (NO USER INPUT)
            idea = agi.generate_idea()

            # 2. FILTER IDEA QUALITY
            if not self._is_strong_idea(idea):
                continue

            # 3. CREATE CONTENT RESPONSE
            response = agi.expand_idea(idea)

            # 4. BUILD VIDEO
            video_path = video_pipeline.create_simple_video(
                response[:200],
                output_name=f"auto_{int(time.time())}.mp4"
            )

            # 5. GROWTH PACKAGING
            growth_pack = growth.build(idea, response)

            # 6. SEND TO N8N (FULL PIPELINE)
            payload = {
                "idea": idea,
                "response": response,
                "video_path": video_path,
                "growth": growth_pack,
                "autopilot": True
            }

            self._send(payload)

            # 7. WAIT BEFORE NEXT CYCLE
            time.sleep(random.randint(300, 900))  # 5–15 min loop

    # -------------------------
    # QUALITY FILTER
    # -------------------------
    def _is_strong_idea(self, idea):
        bad = ["test", "hello", "random", ""]
        return idea and idea.lower() not in bad

    # -------------------------
    # SEND TO N8N
    # -------------------------
    def _send(self, payload):
        try:
            requests.post(self.n8n_url, json=payload, timeout=10)
        except Exception as e:
            print("Autopilot send error:", e)
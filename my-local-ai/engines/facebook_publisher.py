import os
import requests

class FacebookPublisher:

    def __init__(self):
        self.token = os.getenv("FACEBOOK_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")

    def post_video(self, video_path, message):
        if not self.token or not self.page_id:
            return {"status": "disabled", "reason": "missing credentials"}

        try:
            url = f"https://graph.facebook.com/{self.page_id}/videos"

            with open(video_path, "rb") as video_file:
                files = {
                    "source": video_file
                }

                data = {
                    "access_token": self.token,
                    "description": message
                }

                response = requests.post(url, files=files, data=data)

            return response.json()

        except Exception as e:
            return {"status": "error", "message": str(e)}
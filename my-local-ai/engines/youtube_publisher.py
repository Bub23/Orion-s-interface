import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

class YouTubePublisher:

    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.client_secret = "client_secret.json"

    def authenticate(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secret,
            self.scopes
        )

        creds = flow.run_local_server(port=0)

        return build("youtube", "v3", credentials=creds)

    def upload_video(self, video_path, title, description):

        try:
            youtube = self.authenticate()

            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "categoryId": "10"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                },
                media_body=MediaFileUpload(video_path)
            )

            response = request.execute()

            return {
                "status": "success",
                "video_id": response.get("id")
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
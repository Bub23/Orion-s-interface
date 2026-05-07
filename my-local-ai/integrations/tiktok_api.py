import requests

class TikTokAPI:
    """TikTok API integration for content posting."""
    
    def __init__(self, client_id, client_secret, access_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.api_url = "https://open.tiktokapis.com"
    
    def test_connection(self):
        """Test TikTok API connection."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_url}/v1/user/info/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "Connected",
                    "user": user_data.get("data", {}).get("user", {}).get("display_name")
                }
            else:
                return {
                    "status": "Failed",
                    "error": response.json().get("message", "Unknown error")
                }
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def post_video(self, caption, video_url):
        """Post video to TikTok."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "data": {
                    "caption": caption,
                    "video_url": video_url,
                    "disable_comment": False,
                    "disable_duet": False,
                    "disable_stitch": False
                }
            }
            
            url = f"{self.api_url}/v1/post/publish/"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                post_data = response.json()
                return {
                    "success": True,
                    "post_id": post_data.get("data", {}).get("video_id"),
                    "status": "Posted"
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("message", "Failed to post")
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_info(self):
        """Get TikTok user profile info."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_url}/v1/user/info/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                return {"error": response.json()}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_video_analytics(self, video_id):
        """Get analytics for a posted video."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_url}/v1/video/query/"
            params = {"video_id": video_id}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                return {"error": response.json()}
        
        except Exception as e:
            return {"error": str(e)}

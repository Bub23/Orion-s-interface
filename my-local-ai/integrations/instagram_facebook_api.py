import requests

class InstagramFacebookAPI:
    """Instagram/Facebook Graph API integration."""
    
    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.graph_url = "https://graph.instagram.com"
        self.fb_url = "https://graph.facebook.com"
    
    def post_to_facebook(self, message, link=None):
        """Post to Facebook page."""
        try:
            url = f"{self.fb_url}/{self.page_id}/feed"
            payload = {
                "message": message,
                "access_token": self.access_token
            }
            
            if link:
                payload["link"] = link
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "post_id": response.json().get("id")}
            else:
                return {"error": response.json()}
        except Exception as e:
            return {"error": str(e)}
    
    def post_to_instagram(self, caption, image_url=None, video_url=None):
        """Post to Instagram."""
        try:
            # Get Instagram Business Account ID from Facebook Page
            page_url = f"{self.fb_url}/{self.page_id}?fields=instagram_business_account&access_token={self.access_token}"
            page_response = requests.get(page_url, timeout=10)
            
            if page_response.status_code != 200:
                return {"error": "Could not retrieve Instagram account"}
            
            ig_account_id = page_response.json().get("instagram_business_account", {}).get("id")
            if not ig_account_id:
                return {"error": "No Instagram account linked"}
            
            # Create media container
            url = f"{self.graph_url}/{ig_account_id}/media"
            
            payload = {
                "caption": caption,
                "access_token": self.access_token
            }
            
            if image_url:
                payload["image_url"] = image_url
            elif video_url:
                payload["video_url"] = video_url
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                media_id = response.json().get("id")
                # Publish the media
                publish_url = f"{self.graph_url}/{ig_account_id}/media_publish"
                publish_payload = {
                    "creation_id": media_id,
                    "access_token": self.access_token
                }
                publish_response = requests.post(publish_url, json=publish_payload, timeout=10)
                
                if publish_response.status_code == 200:
                    return {"success": True, "post_id": publish_response.json().get("id")}
                else:
                    return {"error": publish_response.json()}
            else:
                return {"error": response.json()}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_instagram_insights(self):
        """Get Instagram account insights."""
        try:
            page_url = f"{self.fb_url}/{self.page_id}?fields=instagram_business_account&access_token={self.access_token}"
            page_response = requests.get(page_url, timeout=10)
            
            if page_response.status_code != 200:
                return {"error": "Could not retrieve Instagram account"}
            
            ig_account_id = page_response.json().get("instagram_business_account", {}).get("id")
            if not ig_account_id:
                return {"error": "No Instagram account linked"}
            
            url = f"{self.graph_url}/{ig_account_id}?fields=insights.metric(impressions,reach,profile_views)&access_token={self.access_token}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json()}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_page_insights(self):
        """Get Facebook page insights."""
        try:
            url = f"{self.fb_url}/{self.page_id}/insights?metric=page_views,page_fans&access_token={self.access_token}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json()}
        
        except Exception as e:
            return {"error": str(e)}
    
    def test_connection(self):
        """Test API connection."""
        try:
            url = f"{self.fb_url}/{self.page_id}?access_token={self.access_token}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return {"status": "Connected", "page_name": response.json().get("name")}
            else:
                return {"status": "Failed", "error": response.json()}
        
        except Exception as e:
            return {"status": "Error", "error": str(e)}

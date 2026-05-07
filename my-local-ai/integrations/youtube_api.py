from googleapiclient.discovery import build
from integrations.youtube_auth import YouTubeAuth

class YouTubeAPI:
    """YouTube API integration for Orion."""
    
    def __init__(self):
        self.auth = YouTubeAuth()
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize YouTube service."""
        credentials = self.auth.get_credentials()
        if credentials:
            self.service = build('youtube', 'v3', credentials=credentials)
    
    def is_authenticated(self):
        """Check if authenticated."""
        return self.service is not None
    
    def get_auth_url(self):
        """Get OAuth URL."""
        return self.auth.get_auth_url()
    
    def handle_callback(self, code):
        """Handle OAuth callback."""
        self.auth.handle_callback(code)
        self._init_service()
    
    def get_channel_info(self):
        """Get channel info."""
        if not self.service:
            return None
        
        try:
            request = self.service.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            return response['items'][0] if response['items'] else None
        except Exception as e:
            return {"error": str(e)}
    
    def upload_video(self, title, description, file_path, tags=None):
        """Upload video to YouTube."""
        if not self.service:
            return {"error": "Not authenticated"}
        
        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '24'  # Entertainment
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
            
            request = self.service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=file_path
            )
            
            response = request.execute()
            return {"success": True, "video_id": response['id']}
        except Exception as e:
            return {"error": str(e)}
    
    def create_playlist(self, title, description):
        """Create a new playlist."""
        if not self.service:
            return {"error": "Not authenticated"}
        
        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description
                }
            }
            
            request = self.service.playlists().insert(
                part='snippet',
                body=body
            )
            
            response = request.execute()
            return {"success": True, "playlist_id": response['id']}
        except Exception as e:
            return {"error": str(e)}
    
    def get_channel_videos(self, limit=10):
        """Get recent videos from channel."""
        if not self.service:
            return {"error": "Not authenticated"}
        
        try:
            channel = self.get_channel_info()
            if not channel:
                return {"error": "No channel found"}
            
            upload_id = channel['contentDetails']['relatedPlaylists']['uploads']
            
            request = self.service.playlistItems().list(
                part='snippet',
                playlistId=upload_id,
                maxResults=limit
            )
            
            response = request.execute()
            videos = []
            for item in response['items']:
                videos.append({
                    'title': item['snippet']['title'],
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'published_at': item['snippet']['publishedAt']
                })
            
            return videos
        except Exception as e:
            return {"error": str(e)}

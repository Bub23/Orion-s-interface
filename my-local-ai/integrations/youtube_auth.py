import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

class YouTubeAuth:
    """Handle YouTube OAuth authentication."""
    
    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:5000/auth/youtube/callback")
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        self.token_file = "youtube_token.pickle"
    
    def get_flow(self):
        """Create OAuth flow."""
        client_config = {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(client_config, scopes=self.scopes)
        flow.redirect_uri = self.redirect_uri
        return flow
    
    def get_auth_url(self):
        """Get authorization URL."""
        flow = self.get_flow()
        auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
        return auth_url, state
    
    def handle_callback(self, code):
        """Handle OAuth callback."""
        flow = self.get_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        self._save_credentials(credentials)
        
        return credentials
    
    def get_credentials(self):
        """Get stored credentials."""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                credentials = pickle.load(f)
            
            if credentials and credentials.expired:
                credentials.refresh(Request())
            
            return credentials
        return None
    
    def _save_credentials(self, credentials):
        """Save credentials to file."""
        with open(self.token_file, 'wb') as f:
            pickle.dump(credentials, f)

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyIntegration:
    """Spotify integration for Orion."""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp = None
        self.setup()
    
    def setup(self):
        """Setup Spotify client."""
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            return True
        except Exception as e:
            print(f"Spotify setup error: {e}")
            return False
    
    def get_current_song(self):
        """Get currently playing song (requires user auth)."""
        if not self.sp:
            return None
        
        try:
            current = self.sp.current_playback()
            if current and current['item']:
                return {
                    "artist": current['item']['artists'][0]['name'],
                    "track": current['item']['name'],
                    "album": current['item']['album']['name'],
                    "playing": current['is_playing']
                }
        except Exception as e:
            return None
    
    def search_track(self, query):
        """Search for a track."""
        if not self.sp:
            return []
        
        try:
            results = self.sp.search(q=query, type='track', limit=5)
            
            tracks = []
            for item in results['tracks']['items']:
                tracks.append({
                    "name": item['name'],
                    "artist": item['artists'][0]['name'],
                    "uri": item['uri'],
                    "url": item['external_urls']['spotify']
                })
            
            return tracks
        except Exception as e:
            return []
    
    def get_recommendations(self, seed_tracks=None):
        """Get track recommendations."""
        if not self.sp or not seed_tracks:
            return []
        
        try:
            results = self.sp.recommendations(seed_tracks=seed_tracks[:5], limit=5)
            
            recommendations = []
            for item in results['tracks']:
                recommendations.append({
                    "name": item['name'],
                    "artist": item['artists'][0]['name'],
                    "url": item['external_urls']['spotify']
                })
            
            return recommendations
        except Exception as e:
            return []

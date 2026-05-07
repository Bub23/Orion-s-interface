from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class CalendarIntegration:
    """Google Calendar integration for Orion."""
    
    def __init__(self, credentials_json=None):
        self.credentials = credentials_json
        self.service = None
        self.setup()
    
    def setup(self):
        """Setup Google Calendar client."""
        try:
            if self.credentials:
                if isinstance(self.credentials, str):
                    import json
                    creds_dict = json.loads(self.credentials)
                else:
                    creds_dict = self.credentials
                
                creds = Credentials.from_service_account_info(creds_dict)
                self.service = build('calendar', 'v3', credentials=creds)
                return True
        except Exception as e:
            print(f"Calendar setup error: {e}")
        
        return False
    
    def create_event(self, summary, start_time, end_time=None, description=""):
        """Create a calendar event."""
        if not self.service:
            return {"success": False, "error": "Calendar not connected"}
        
        try:
            if not end_time:
                end_time = (datetime.fromisoformat(start_time.replace('Z', '+00:00')) + timedelta(hours=1)).isoformat()
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "event_id": event['id'],
                "url": event['htmlLink']
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_upcoming_events(self, limit=5):
        """Get upcoming events."""
        if not self.service:
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=limit,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            results = []
            for event in events:
                results.append({
                    "summary": event.get('summary'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "description": event.get('description', '')
                })
            
            return results
        except Exception as e:
            return []
    
    def is_available(self, start_time, end_time):
        """Check if time slot is available."""
        if not self.service:
            return False
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True
            ).execute()
            
            conflicts = events_result.get('items', [])
            return len(conflicts) == 0
        except:
            return False

import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes must match the email_engine perfectly
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def authenticate_calendar():
    """Authenticates the user and returns the Calendar service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def fetch_upcoming_events(service, max_results=5):
    """Fetches the next upcoming events from the primary calendar."""
    try:
        # Get the current time in UTC format required by the API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        parsed_events = []
        for event in events:
            # Handle both timed events and all-day events
            start = event['start'].get('dateTime', event['start'].get('date'))
            parsed_events.append({
                "summary": event.get('summary', 'Busy / Private Event'),
                "start": start
            })
        return parsed_events
        
    except Exception as error:
        return [{"error": str(error)}]

if __name__ == '__main__':
    # Run this file directly to trigger the new OAuth handshake
    print("Initializing Authentication...")
    cal_service = authenticate_calendar()
    print("Authentication Successful. Fetching events...\n")
    events = fetch_upcoming_events(cal_service)
    for e in events:
        print(e)
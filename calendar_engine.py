import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Adjust this if your code uses a different calendar scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_calendar():
    creds = None
    has_cloud_secrets = False
    
    # 1. Safely check for Cloud Secrets without crashing locally
    try:
        if "calendar_token" in st.secrets:
            has_cloud_secrets = True
    except Exception:
        has_cloud_secrets = False
        
    # 2. Cloud Deployment Execution
    if has_cloud_secrets:
        creds_info = {
            "token": st.secrets["calendar_token"]["token"],
            "refresh_token": st.secrets["calendar_token"]["refresh_token"],
            "token_uri": st.secrets["calendar_token"]["token_uri"],
            "client_id": st.secrets["calendar_token"]["client_id"],
            "client_secret": st.secrets["calendar_token"]["client_secret"],
            "scopes": SCOPES
        }
        creds = Credentials.from_authorized_user_info(creds_info)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
    # 3. Local Environment: Fallback to the local JSON files
    else:
        # Change 'token_calendar.json' to 'token.json' if you only use one combined token file locally
        token_file = 'token_calendar.json' 
        
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

    # Build and return the service
    return build('calendar', 'v3', credentials=creds)

# --- KEEP YOUR OTHER CALENDAR FUNCTIONS DOWN HERE (like fetch_events) ---
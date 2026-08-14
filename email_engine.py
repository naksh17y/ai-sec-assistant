import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    
    # 1. Cloud Deployment: Try to load from Streamlit Secrets first
    if "gmail_token" in st.secrets:
        creds_info = {
            "token": st.secrets["gmail_token"]["token"],
            "refresh_token": st.secrets["gmail_token"]["refresh_token"],
            "token_uri": st.secrets["gmail_token"]["token_uri"],
            "client_id": st.secrets["gmail_token"]["client_id"],
            "client_secret": st.secrets["gmail_token"]["client_secret"],
            "scopes": SCOPES
        }
        creds = Credentials.from_authorized_user_info(creds_info)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
    # 2. Local Environment: Fallback to the local files
    else:
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

    # Build and return the service
    service = build('gmail', 'v1', credentials=creds)
    return service
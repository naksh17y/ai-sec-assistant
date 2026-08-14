import os
import base64
import streamlit as st
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    has_cloud_secrets = False
    
    # 1. Safely check for Cloud Secrets without crashing locally
    try:
        if "gmail_token" in st.secrets:
            has_cloud_secrets = True
    except Exception:
        has_cloud_secrets = False
        
    # 2. Cloud Deployment Execution
    if has_cloud_secrets:
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
            
    # 3. Local Environment: Fallback to the local JSON files
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
    return build('gmail', 'v1', credentials=creds)

def extract_body(payload):
    """Helper function to parse the email body and strip HTML."""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                return BeautifulSoup(html, 'html.parser').get_text(separator=' ', strip=True)
    elif 'body' in payload and 'data' in payload['body']:
        data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        if payload['mimeType'] == 'text/html':
            return BeautifulSoup(data, 'html.parser').get_text(separator=' ', strip=True)
        return data
    return "No text body content found."

def fetch_latest_emails(service, max_results=3):
    """Fetches the latest emails from the inbox for security auditing."""
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    parsed_emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        payload = msg['payload']
        headers = payload.get('headers', [])
        
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        
        body = extract_body(payload)
        
        parsed_emails.append({
            'sender': sender,
            'subject': subject,
            'body': body[:2000] # Limiting size to prevent blowing out the AI context window
        })
        
    return parsed_emails

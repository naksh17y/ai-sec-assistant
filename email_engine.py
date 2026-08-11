import os.path
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import threat_engine
import ai_engine

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def authenticate_gmail():
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
    return build('gmail', 'v1', credentials=creds)

def get_email_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            body += get_email_body(part)
    elif 'body' in payload and 'data' in payload['body']:
        data = payload['body']['data']
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data).decode('utf-8', errors='ignore')
        body += decoded_data
    return body

def fetch_latest_emails(service, max_results=3):
    """Fetches emails and returns a list of dictionaries containing all analysis."""
    analyzed_emails = [] # We will store our data here instead of just printing it
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
        messages = results.get('messages', [])

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            
            raw_body = get_email_body(payload)
            soup = BeautifulSoup(raw_body, 'html.parser')
            clean_text = soup.get_text(separator=' ', strip=True)
            links = [a['href'] for a in soup.find_all('a', href=True)]
            
            # AI Analysis
            ai_analysis = ai_engine.analyze_email(sender, subject, clean_text[:800])
            
            # Threat Detection
            risk_score, details = 0.0, "No URLs found"
            if links:
                risk_score, details = threat_engine.calculate_url_risk(links[0])
            
            # Package the data for the UI
            email_data = {
                "sender": sender,
                "subject": subject,
                "category": ai_analysis.get('Category', 'Unknown'),
                "action_required": ai_analysis.get('Action_Required', 'Unknown'),
                "summary": ai_analysis.get('Summary', 'AI Error'),
                "risk_score": risk_score,
                "url_scanned": links[0] if links else "None"
            }
            analyzed_emails.append(email_data)
            
        return analyzed_emails

    except Exception as error:
        return [{"error": str(error)}]

if __name__ == '__main__':
    # Quick CLI test to ensure it still works
    gmail_service = authenticate_gmail()
    data = fetch_latest_emails(gmail_service)
    print(f"Successfully processed {len(data)} emails.")
import os
import streamlit as st
from google import genai
from dotenv import load_dotenv

# Load local .env variables if running on your home computer
load_dotenv()

def get_gemini_client():
    api_key = None
    
    # 1. Cloud Deployment: Check Streamlit Secrets safely
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    # 2. Local Environment: Fall back to .env file
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        
    # 3. Initialize the client
    if not api_key:
        raise ValueError("API key not found. Please set GEMINI_API_KEY in Streamlit Secrets or a local .env file.")
        
    return genai.Client(api_key=api_key)

# --- KEEP YOUR OTHER CHATBOT FUNCTIONS DOWN HERE ---
def generate_response(prompt):
    client = get_gemini_client()
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    return response.text
    
def chat_with_assistant(user_message, history="", schedule_context=""):
    """A general purpose chatbot function that maintains context and schedule awareness."""
    if not GEMINI_API_KEY:
        return "API key not configured in environment."

    prompt = f"""
    You are an elite Cybersecurity Executive Assistant. 
    
    Here is the user's upcoming schedule:
    {schedule_context if schedule_context else "No schedule synced yet."}
    
    Use this recent conversation history for context (if any):
    {history}

    User: {user_message}
    Assistant:
    """

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
    
if __name__ == '__main__':
    test_sender = "hr@dreamcompany.com"
    test_subject = "Interview Request: Cybersecurity Analyst"
    test_body = "Hi, we loved your resume and your IoT IDS project. Are you available this Thursday at 2 PM IST for a technical round?"
    
    print("Testing AI Engine...")
    result = analyze_email(test_sender, test_subject, test_body)
    print(json.dumps(result, indent=4))
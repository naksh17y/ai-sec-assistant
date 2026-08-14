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

def chat_with_assistant(prompt, recent_history, context):
    """Generates a response from the AI assistant using the updated SDK."""
    # Grab the securely authenticated client
    client = get_gemini_client()
    
    # Format the context and history for the AI
    system_context = f"System Context (Data/Schedule):\n{context}\n\n" if context else ""
    
    history_text = "Recent Conversation History:\n"
    if recent_history:
        for msg in recent_history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_text += f"{role}: {msg.get('content')}\n"
    else:
        history_text += "No recent history.\n"
        
    full_prompt = f"{system_context}{history_text}\nUser: {prompt}\nAssistant:"
    
    try:
        # Call the new gemini-3.5-flash model
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

if __name__ == '__main__':
    test_sender = "hr@dreamcompany.com"
    test_subject = "Interview Request: Cybersecurity Analyst"
    test_body = "Hi, we loved your resume and your IoT IDS project. Are you available this Thursday at 2 PM IST for a technical round?"
    
    print("Testing AI Engine...")
    result = chat_with_assistant(test_sender, test_subject, test_body)
    print(json.dumps(result, indent=4))
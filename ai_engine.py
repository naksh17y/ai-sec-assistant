import os
import json
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
    # Ensure recent_history is a list before iterating to prevent crashes
    if recent_history and isinstance(recent_history, list):
        for msg in recent_history:
            # Safely handle dictionaries
            if isinstance(msg, dict):
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content')}\n"
    else:
        history_text += "No recent history.\n"
        
    full_prompt = f"{system_context}{history_text}\nUser: {prompt}\nAssistant:"
    
    try:
        # Fixed the model name to a valid Gemini version
        response = client.models.generate_content(
            model='gemini-3.0-flash',
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

if __name__ == '__main__':
    # Fixed the test parameters to match what the function actually expects
    test_prompt = "Hi, I am preparing for a technical round for a Cybersecurity Analyst role. Any tips?"
    test_history = [{"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hi there! How can I help you today?"}]
    test_context = "User is Nakshatra Kale. They recently built an IoT Intrusion Detection System."
    
    print("Testing AI Engine...")
    result = chat_with_assistant(test_prompt, test_history, test_context)
    print(result)
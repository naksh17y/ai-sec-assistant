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
    """Generates a response from the AI assistant with automatic fallback for high demand."""
    client = get_gemini_client()
    
    # Format context and history
    system_context = f"System Context (Data/Schedule):\n{context}\n\n" if context else ""
    
    history_text = "Recent Conversation History:\n"
    if recent_history and isinstance(recent_history, list):
        for msg in recent_history:
            if isinstance(msg, dict):
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content')}\n"
    else:
        history_text += "No recent history.\n"
        
    full_prompt = f"{system_context}{history_text}\nUser: {prompt}\nAssistant:"
    
    # Models to try in order if Google's servers are overloaded (503)
    candidate_models = [
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-2.5-flash-lite'
    ]
    
    last_error = None
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            # If it's a temporary 503 overload, loop to the next model
            continue

    return f"Error communicating with AI: {str(last_error)}"

if __name__ == '__main__':
    # Fixed the test parameters to match what the function actually expects
    test_prompt = "Hi, I am preparing for a technical round for a Cybersecurity Analyst role. Any tips?"
    test_history = [{"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hi there! How can I help you today?"}]
    test_context = "User is Nakshatra Kale. They recently built an IoT Intrusion Detection System."
    
    print("Testing AI Engine...")
    result = chat_with_assistant(test_prompt, test_history, test_context)
    print(result)
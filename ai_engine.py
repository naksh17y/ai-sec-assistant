import json
from google import genai

# Best practice: Use environment variables in production
GEMINI_API_KEY = "INSERT_YOUR_GEMINI_KEY_HERE"

# The new SDK uses a Client instantiation model
client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_email(sender, subject, body_snippet):
    """Analyzes an email using AI to categorize and summarize it."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return {"error": "API key not configured"}

    prompt = f"""
    You are an elite Executive Assistant and Cybersecurity Analyst.
    Analyze the following email and return a structured JSON response.

    Email Sender: {sender}
    Email Subject: {subject}
    Email Body Snippet: {body_snippet}

    Respond ONLY with a valid JSON object using this exact format. Do not include markdown formatting:
    {{
        "Category": "High Priority | Schedule | Informational | Transactional | Suspicious",
        "Action_Required": "Yes | No",
        "Summary": "A strict 1-to-2 sentence summary of the email."
    }}
    """

    try:
        # We use the updated client.models.generate_content syntax
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        response_text = response.text.strip()
        
        # Clean up the response in case the LLM wraps it in markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]

        return json.loads(response_text.strip())
        
    except Exception as e:
        return {"error": f"LLM parsing failed: {str(e)}"}
    
def chat_with_assistant(user_message, history="", schedule_context=""):
    """A general purpose chatbot function that maintains context and schedule awareness."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return "API key not configured."

    # We inject the calendar data directly into the system instructions
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
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
    # We feed the LLM its persona and the recent chat history
    prompt = f"""
    You are an elite Cybersecurity Executive Assistant. 
    Use this recent conversation history for context (if any):
    {history}

    User: {user_message}
    Assistant:
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
    
# Test the engine directly
if __name__ == '__main__':
    test_sender = "hr@dreamcompany.com"
    test_subject = "Interview Request: Cybersecurity Analyst"
    test_body = "Hi, we loved your resume and your IoT IDS project. Are you available this Thursday at 2 PM IST for a technical round?"
    
    print("Testing AI Engine...")
    result = analyze_email(test_sender, test_subject, test_body)
    print(json.dumps(result, indent=4))
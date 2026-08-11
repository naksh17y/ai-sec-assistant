import base64
import requests

# Best practice: In production, this would be loaded from environment variables (.env)
VT_API_KEY = "INSERT_YOUR_VIRUSTOTAL_KEY_HERE"

def calculate_url_risk(url):
    """
    Scans a URL against VirusTotal and calculates a risk percentage.
    """
    if not VT_API_KEY or VT_API_KEY == "YOUR_VIRUSTOTAL_API_KEY":
        return 0, "API key not configured"

    # VirusTotal v3 requires the URL to be base64url encoded without the '=' padding
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    
    url_endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }
    
    try:
        response = requests.get(url_endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            
            total_engines = malicious + suspicious + harmless + undetected
            
            if total_engines == 0:
                return 0, "No historical scan data"
            
            # Calculate Risk Percentage based on engines flagging it as bad
            bad_flags = malicious + suspicious
            risk_percentage = (bad_flags / total_engines) * 100
            
            return round(risk_percentage, 2), stats
        elif response.status_code == 404:
            return 0, "URL never scanned by VirusTotal before"
        else:
            return 0, f"API Error: {response.status_code}"
            
    except Exception as e:
        return 0, f"Connection error: {str(e)}"

# Test the engine directly
if __name__ == '__main__':
    test_url = "http://google.com"
    print(f"Scanning: {test_url}")
    risk_score, details = calculate_url_risk(test_url)
    print(f"Risk Score: {risk_score}%")
    print(f"Details: {details}")
import requests
import json
import os
from datetime import datetime, timedelta

ACCESS_TOKEN_FILE = "/app/access_token.json"  # Inside Docker
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

def load_access_token():
    """Load access token and its expiration timestamp from file."""
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, "r") as file:
            data = json.load(file)
            return data.get("access_token"), data.get("expires_at")
    return None, None

def save_access_token(token):
    """Save access token and next refresh timestamp to file."""
    expires_at = (datetime.utcnow() + timedelta(days=60)).isoformat()  # Meta tokens last ~60 days
    with open(ACCESS_TOKEN_FILE, "w") as file:
        json.dump({"access_token": token, "expires_at": expires_at}, file)

def refresh_access_token():
    """Refresh and update long-lived access token."""
    current_token, expires_at = load_access_token()
    if not current_token:
        print("No saved token found. Generate a new one manually.")
        return
    
    # Check if token is near expiry
    if expires_at:
        expiry_time = datetime.fromisoformat(expires_at)
        days_left = (expiry_time - datetime.utcnow()).days
        if days_left > 10:
            print(f"Token still valid for {days_left} days. No refresh needed.")
            return

    url = f"https://graph.facebook.com/v22.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={current_token}"
    
    response = requests.get(url).json()
    
    if "access_token" in response:
        new_token = response["access_token"]
        save_access_token(new_token)
        print("🔄 Access token refreshed successfully!")
    else:
        print("⚠️ Error refreshing token:", response)

if __name__ == "__main__":
    refresh_access_token()

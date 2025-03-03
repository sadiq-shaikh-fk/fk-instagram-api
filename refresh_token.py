import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_FILE = "access_token.json"

def load_access_token():
    """Load access token from .env first, then from JSON file."""
    token = os.getenv("ACCESS_TOKEN")  # Load from .env
    if token:
        return token

    # Fallback: Load from access_token.json
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, "r") as file:
            return json.load(file).get("access_token")
    
    return None

def save_access_token(token):
    """Save access token to .env and access_token.json."""
    # Update .env file
    with open(".env", "a") as file:
        file.write(f"\nACCESS_TOKEN={token}")

    # Save as backup in JSON file
    with open(ACCESS_TOKEN_FILE, "w") as file:
        json.dump({"access_token": token}, file)

# Test loading the token
if __name__ == "__main__":
    token = load_access_token()
    if token:
        print("✅ Token loaded successfully!")
    else:
        print("⚠️ No token found. Please generate one.")

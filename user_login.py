from fastapi import FastAPI, Request
import requests
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI App
app = FastAPI()

# Database connection
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST")
)
cursor = conn.cursor()

# Exchange Short-lived Token for Long-lived Token
def get_long_lived_token(short_token):
    url = f"https://graph.facebook.com/v22.0/oauth/access_token?grant_type=fb_exchange_token&client_id={os.getenv('APP_ID')}&client_secret={os.getenv('APP_SECRET')}&fb_exchange_token={short_token}"
    response = requests.get(url).json()
    return response.get("access_token")

# Get Facebook User ID
def get_facebook_user_id(access_token):
    url = f"https://graph.facebook.com/v22.0/me?fields=id&access_token={access_token}"
    response = requests.get(url).json()
    return response.get("id")

# Handle Authentication Callback
@app.get("/auth/callback")
def auth_callback(request: Request):
    short_token = request.query_params.get("token")

    if not short_token:
        return {"error": "No access token provided"}

    # Exchange short-lived token for long-lived token
    long_token = get_long_lived_token(short_token)

    if not long_token:
        return {"error": "Failed to exchange token"}

    # Get user ID
    fb_user_id = get_facebook_user_id(long_token)

    if not fb_user_id:
        return {"error": "Failed to get user ID"}

    # Store token in database
    cursor.execute(
        """
        INSERT INTO user_tokens (fb_user_id, access_token) 
        VALUES (%s, %s) 
        ON CONFLICT (fb_user_id) 
        DO UPDATE SET access_token = EXCLUDED.access_token, created_at = NOW();
        """,
        (fb_user_id, long_token)
    )
    conn.commit()

    return {"message": "User authenticated successfully!", "fb_user_id": fb_user_id, "long_lived_token": long_token}

from fastapi import FastAPI, Query
import requests
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Instagram API credentials from .env file
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  
INSTAGRAM_USER_ID =os.getenv("INSTAGRAM_USER_ID")

# Route to fetch Instagram business profile
@app.get("/profile")
async def get_instagram_profile(
    ig_username: str = Query(..., description="Instagram username"),
    media: bool = Query(False, description="Include posts (media) data"),
    insights: bool = Query(False, description="Include post insights"),
    stories: bool = Query(False, description="Include stories data"),
    reels: bool = Query(False, description="Include reels data")
    ):
  
    # Base API fields (Profile Info)
    fields = "id,username,name,profile_picture_url,biography,followers_count,follows_count,media_count,website,legacy_instagram_user_id,shopping_product_tag_eligibility"
    
    # If media=true, add media fields
    if media:
        fields += ",media{media_type,media_url,caption,timestamp,permalink,like_count,comments_count,id,children{media_type,media_url}}"

    # If stories=true, fetch IG Stories
    if stories:
        fields += ",stories{id,media_type,media_url,caption,timestamp}"

    # If reels=true, fetch IG Reels
    if reels:
        fields += ",media{media_type,media_url,caption,timestamp,permalink,like_count,comments_count,id}"

    # Construct the API request URL
    url = f"https://graph.facebook.com/v22.0/{INSTAGRAM_USER_ID}?fields=business_discovery.username({ig_username}){{{fields}}}&access_token={ACCESS_TOKEN}"

    #send request to Instagram API
    response = requests.get(url)
    data = response.json()

    #error handling from api response
    if "error" in data:
        return {"error":data["error"]["message"]}
    
    # Extract business profile details
    profile = data.get("business_discovery", {})

    response_data = {
        "ig_user_id": profile.get("id", ""),
        "ig_name": profile.get("name", ""),
        "ig_username": profile.get("username", ""),
        "ig_bio": profile.get("biography", ""),
        "website": profile.get("website", ""),
        "legacy_instagram_user_id": profile.get("legacy_instagram_user_id", ""),
        "profile_picture_url": profile.get("profile_picture_url", ""),
        "shopping_product_tag_eligibility": profile.get("shopping_product_tag_eligibility", ""),
        "followers_count": profile.get("followers_count", ""),
        "follows_count": profile.get("follows_count", ""),
        "media_count": profile.get("media_count", "")
    }

    # If media=true, add media posts
    if media:
        response_data["posts"] = profile.get("media", {}).get("data", [])

    # If stories=true, add stories data
    if stories:
        response_data["stories"] = profile.get("stories", {}).get("data", [])

    # If reels=true, add reels data
    if reels:
        response_data["reels"] = [post for post in profile.get("media", {}).get("data", []) if post.get("media_type") == "VIDEO"]

    # If insights=true, fetch insights for each post
    if insights and media:
        post_insights = {}
        for post in response_data["posts"]:
            post_id = post["id"]
            insights_url = f"https://graph.facebook.com/v22.0/{post_id}/insights?metric=impressions,reach,engagement,saved,video_views&access_token={ACCESS_TOKEN}"
            insights_response = requests.get(insights_url).json()
            post_insights[post_id] = insights_response

        response_data["post_insights"] = post_insights

    return response_data

@app.get("/post")
async def get_post_details(
    post_id: str = Query(..., description="Instagram Post ID")
):
    """
    Fetch more details of a specific Instagram post using its ID.
    Example: /post?post_id=17989502348771838
    """
    url = f"https://graph.facebook.com/v22.0/{post_id}?fields=id,media_type,media_url,owner,timestamp,caption,comments_count,is_comment_enabled,like_count,insights.metric(impressions,reach,engagement,saved,video_views)&access_token={ACCESS_TOKEN}"

    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return {"error": data["error"]["message"]}

# App will run on port 7000
# to run the app, use command: uvicorn app:app --reload --port 7000

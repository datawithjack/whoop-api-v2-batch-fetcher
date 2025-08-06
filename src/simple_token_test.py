import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_token_refresh():
    """Test token refresh following exact WHOOP API documentation"""
    
    # Load batch credentials
    with open(".whoop_credentials_batch.json", "r") as f:
        batch_credentials = json.load(f)
    
    user_email = "jackfrankandrew@gmail.com"
    credentials = batch_credentials[user_email]
    
    print(f"Testing token refresh for: {user_email}")
    
    # Get environment variables
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Refresh Token: {credentials['refresh_token'][:20]}...")
    
    # WHOOP token refresh endpoint
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    
    # Prepare refresh request (including redirect_uri as it might be required)
    refresh_data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "offline",
        "refresh_token": credentials['refresh_token'],
        "redirect_uri": "http://localhost:8080"
    }
    
    print(f"\nRefresh request data:")
    for key, value in refresh_data.items():
        if key in ['client_secret', 'refresh_token']:
            print(f"  {key}: {value[:20]}...")
        else:
            print(f"  {key}: {value}")
    
    try:
        print(f"\nMaking request to: {token_url}")
        response = requests.post(token_url, data=refresh_data)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            token_response = response.json()
            print(f"✅ SUCCESS!")
            print(f"New access token: {token_response.get('access_token', '')[:20]}...")
            print(f"New refresh token: {token_response.get('refresh_token', '')[:20]}...")
            print(f"Expires in: {token_response.get('expires_in')} seconds")
            print(f"Scope: {token_response.get('scope')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_token_refresh()

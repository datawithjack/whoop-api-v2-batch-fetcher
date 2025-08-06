import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_token_refresh_with_uri(redirect_uri):
    """Test token refresh with a specific redirect_uri"""
    
    # Load batch credentials
    with open(".whoop_credentials_batch.json", "r") as f:
        batch_credentials = json.load(f)
    
    user_email = "jackfrankandrew@gmail.com"
    credentials = batch_credentials[user_email]
    
    # Get environment variables
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    
    # WHOOP token refresh endpoint
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    
    # Prepare refresh request (following WHOOP API documentation)
    refresh_data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "offline",  # Required for refresh token flow
        "refresh_token": credentials['refresh_token']
    }
    
    try:
        response = requests.post(token_url, data=refresh_data)
        
        if response.status_code == 200:
            token_response = response.json()
            print(f"✅ SUCCESS with redirect_uri: {redirect_uri}")
            print(f"   New access token: {token_response.get('access_token', '')[:20]}...")
            return True
        else:
            print(f"❌ Failed with redirect_uri: {redirect_uri}")
            print(f"   Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error_description', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return False
                
    except Exception as e:
        print(f"❌ Exception with redirect_uri {redirect_uri}: {e}")
        return False

def test_token_refresh():
    """Test token refresh with different redirect_uri variations"""
    
    print("Testing token refresh with different redirect_uri variations...")
    print("=" * 70)
    
    # Common redirect_uri variations to test
    redirect_uris = [
        "http://localhost:8080",
        "http://localhost:8080/",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8080/",
        "localhost:8080",
        "127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
        "https://localhost:8080",
        "https://127.0.0.1:8080"
    ]
    
    success = False
    for uri in redirect_uris:
        print(f"\nTesting: {uri}")
        if test_token_refresh_with_uri(uri):
            success = True
            print(f"\n🎉 Found working redirect_uri: {uri}")
            print("Update your .env file with this redirect_uri!")
            break
    
    if not success:
        print(f"\n❌ None of the tested redirect_uri variations worked.")
        print("You need to check your WHOOP Developer Console and update your .env file")
        print("with the exact redirect_uri that's whitelisted there.")

if __name__ == "__main__":
    test_token_refresh()

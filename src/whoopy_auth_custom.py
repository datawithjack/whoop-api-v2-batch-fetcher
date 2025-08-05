import asyncio
import json
import os
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def create_whoop_config():
    """Create WHOOP configuration from environment variables"""
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    redirect_uri = os.getenv('WHOOP_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ Missing required environment variables:")
        if not client_id:
            print("   - WHOOP_CLIENT_ID")
        if not client_secret:
            print("   - WHOOP_CLIENT_SECRET")
        if not redirect_uri:
            print("   - WHOOP_REDIRECT_URI")
        print("Please check your .env file")
        return None
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }

def save_config_to_file(config):
    """Save configuration to config.json for whoopy"""
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("✅ Configuration saved to config.json")

def save_credentials(credentials):
    """Save credentials to .whoop_credentials.json"""
    with open(".whoop_credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)
    print("✅ Credentials saved to .whoop_credentials.json")

async def custom_whoop_auth():
    """Custom WHOOP authentication following official OAuth 2.0 flow"""
    print("🔐 Custom WHOOP Authentication (Official OAuth 2.0)")
    print("="*60)
    
    # Create configuration
    config = create_whoop_config()
    if not config:
        return False
    
    # Save config for whoopy
    save_config_to_file(config)
    
    # Define scopes according to WHOOP documentation
    # The 'offline' scope is REQUIRED to receive refresh tokens
    scopes = ["read:recovery", "read:sleep", "read:workout", "read:profile", "offline"]
    scope_string = " ".join(scopes)
    
    print("📋 Requesting scopes (following WHOOP OAuth documentation):")
    for scope in scopes:
        if scope == "offline":
            print(f"   - {scope} (REQUIRED for refresh tokens)")
        else:
            print(f"   - {scope}")
    print()
    
    # Step 1: Create authorization URL (following WHOOP docs)
    auth_url = "https://api.prod.whoop.com/oauth/oauth2/auth"
    auth_params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "scope": scope_string,
        "state": "custom_auth_flow_" + str(int(datetime.now().timestamp()))
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(auth_params)}"
    
    print("🔐 Opening browser for authorization...")
    print(f"📋 Authorization URL: {auth_url_with_params}")
    print()
    print("📝 After authorization, you'll be redirected to your redirect URI")
    print("📝 Copy the entire URL from your browser and paste it below")
    print()
    
    # Open browser
    webbrowser.open(auth_url_with_params)
    
    # Step 2: Get authorization code from user
    print("📋 Paste the redirect URL here:")
    redirect_url = input().strip()
    
    # Parse the redirect URL to get the authorization code
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    # Check for errors
    if 'error' in query_params:
        error = query_params['error'][0]
        error_desc = query_params.get('error_description', [''])[0]
        print(f"❌ Authorization failed: {error}")
        print(f"   Description: {error_desc}")
        if error == "invalid_scope":
            print("💡 This means your WHOOP app doesn't have permission for the requested scopes")
            print("💡 Contact WHOOP to add the required scopes to your app")
        return False
    
    # Get authorization code
    if 'code' not in query_params:
        print("❌ No authorization code found in redirect URL")
        return False
    
    auth_code = query_params['code'][0]
    print("✅ Authorization code received")
    
    # Step 3: Exchange authorization code for tokens (following WHOOP docs)
    print("🔄 Exchanging authorization code for tokens...")
    
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": auth_code,
        "redirect_uri": config["redirect_uri"]
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_response = response.json()
            
            # Calculate expiration time
            expires_in = token_response.get('expires_in', 3600)
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Check if we got a refresh token
            refresh_token = token_response.get('refresh_token')
            if not refresh_token:
                print("⚠️  WARNING: No refresh token received!")
                print("💡 This means your WHOOP app doesn't have the 'offline' scope")
                print("💡 Contact WHOOP to add the 'offline' scope to your app")
                print("💡 Without refresh tokens, you'll need to re-authenticate manually")
            
            # Create credentials object
            credentials = {
                "access_token": token_response.get('access_token'),
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "token_type": token_response.get('token_type', 'bearer'),
                "scope": token_response.get('scope', scope_string),
                "auth_timestamp": datetime.now().isoformat()
            }
            
            # Save credentials
            save_credentials(credentials)
            
            print("✅ Token exchange successful!")
            print(f"📅 Token expires at: {expires_at}")
            print(f"🔄 Refresh token: {'✅ Available' if refresh_token else '❌ Not Available'}")
            
            if refresh_token:
                print("💡 You can now use refresh tokens to get new access tokens automatically")
            else:
                print("💡 You'll need to re-authenticate manually when tokens expire")
            
            return True
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during token exchange: {e}")
        return False

async def refresh_access_token(refresh_token, config):
    """Refresh access token using refresh token (following WHOOP docs)"""
    print("🔄 Refreshing access token...")
    
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "scope": "offline"  # Include offline scope in refresh request
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_response = response.json()
            
            # Calculate new expiration time
            expires_in = token_response.get('expires_in', 3600)
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Create updated credentials
            credentials = {
                "access_token": token_response.get('access_token'),
                "refresh_token": token_response.get('refresh_token', refresh_token),  # Use new refresh token if provided
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "token_type": token_response.get('token_type', 'bearer'),
                "scope": token_response.get('scope', 'offline'),
                "auth_timestamp": datetime.now().isoformat()
            }
            
            # Save updated credentials
            save_credentials(credentials)
            
            print("✅ Token refresh successful!")
            print(f"📅 New token expires at: {expires_at}")
            return True
            
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during token refresh: {e}")
        return False

async def test_credentials():
    """Test the saved credentials"""
    print("\n🧪 Testing saved credentials...")
    
    try:
        # Load credentials
        with open(".whoop_credentials.json", "r") as f:
            credentials = json.load(f)
        
        # Test API call directly (without whoopy client)
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Test user profile endpoint
        profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ API test successful!")
            print(f"👤 User: {profile_data.get('first_name', 'Unknown')} {profile_data.get('last_name', 'Unknown')}")
            print(f"🆔 WHOOP User ID: {profile_data.get('user_id', 'Unknown')}")
            
            # Also test sleep endpoint
            sleep_url = "https://api.prod.whoop.com/developer/v2/activity/sleep"
            sleep_params = {
                'start': '2024-08-01T00:00:00.000Z',
                'end': '2024-08-02T00:00:00.000Z',
                'limit': 1
            }
            sleep_response = requests.get(sleep_url, headers=headers, params=sleep_params)
            
            if sleep_response.status_code == 200:
                sleep_data = sleep_response.json()
                print(f"😴 Sleep API test successful! Records available: {len(sleep_data.get('records', []))}")
            else:
                print(f"⚠️  Sleep API test failed: {sleep_response.status_code}")
            
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Custom WHOOP Authentication Setup (Official OAuth 2.0)")
    print("="*60)
    
    # Check if credentials already exist
    if os.path.exists(".whoop_credentials.json"):
        print("⚠️  Existing credentials found:")
        print("   - .whoop_credentials.json")
        print("   - config.json")
        
        response = input("Do you want to re-authenticate? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Using existing credentials")
            print("💡 Run: python src/custom_sleep_fetcher.py")
            return
    
    # Run authentication
    success = asyncio.run(custom_whoop_auth())
    
    if success:
        # Test credentials
        test_success = asyncio.run(test_credentials())
        
        if test_success:
            print("\n🎉 Authentication complete!")
            print("💡 You can now run: python src/custom_sleep_fetcher.py")
        else:
            print("\n⚠️  Authentication completed but API test failed")
    else:
        print("\n❌ Authentication failed. Please check your configuration and try again.")

if __name__ == "__main__":
    main() 
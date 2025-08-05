import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def load_credentials():
    """Load saved credentials"""
    try:
        with open(".whoop_credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No credentials file found")
        return None
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def save_credentials(credentials):
    """Save credentials to .whoop_credentials.json"""
    with open(".whoop_credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)
    print("✅ Credentials saved to .whoop_credentials.json")

def is_token_expired(credentials):
    """Check if token is expired or will expire soon (within 5 minutes)"""
    if 'expires_at' not in credentials:
        return True
    
    try:
        expires_at = datetime.fromisoformat(credentials['expires_at'])
        # Consider token expired if it expires within 5 minutes
        buffer_time = timedelta(minutes=5)
        return datetime.now() + buffer_time >= expires_at
    except:
        return True

def refresh_access_token(credentials):
    """Refresh access token using refresh token"""
    print("🔄 Refreshing access token...")
    
    if 'refresh_token' not in credentials:
        print("❌ No refresh token available")
        return False
    
    # Get environment variables
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    redirect_uri = os.getenv('WHOOP_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ Missing environment variables for token refresh")
        return False
    
    # WHOOP token refresh endpoint
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    
    # Prepare refresh request
    refresh_data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": credentials['refresh_token'],
        "redirect_uri": redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=refresh_data)
        
        if response.status_code == 200:
            token_response = response.json()
            
            # Calculate new expiration time
            expires_in = token_response.get('expires_in', 3600)
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Update credentials
            credentials.update({
                "access_token": token_response.get('access_token'),
                "refresh_token": token_response.get('refresh_token', credentials.get('refresh_token')),
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "token_type": token_response.get('token_type', 'bearer'),
                "last_refreshed": datetime.now().isoformat()
            })
            
            # Save updated credentials
            save_credentials(credentials)
            
            print("✅ Token refreshed successfully!")
            print(f"📅 New expiration: {expires_at}")
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

def test_token(credentials):
    """Test if the token is working"""
    print("🧪 Testing token...")
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    # Test with user profile endpoint
    profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
    
    try:
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ Token is valid!")
            print(f"👤 User: {profile_data.get('first_name', 'Unknown')} {profile_data.get('last_name', 'Unknown')}")
            return True
        else:
            print(f"❌ Token test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def handle_token_refresh():
    """Main function to handle token refresh"""
    print("🔄 WHOOP Token Refresh Handler")
    print("="*50)
    
    # Load existing credentials
    credentials = load_credentials()
    if not credentials:
        print("❌ No credentials found. Please run authentication first:")
        print("   python src/whoopy_auth_custom.py")
        return False
    
    print("📋 Current token status:")
    
    # Check if token is expired
    if is_token_expired(credentials):
        print("   ❌ Token is expired or will expire soon")
        
        # Try to refresh the token
        if refresh_access_token(credentials):
            # Test the refreshed token
            if test_token(credentials):
                print("✅ Token refresh successful!")
                return True
            else:
                print("❌ Refreshed token failed test")
        else:
            print("❌ Token refresh failed")
        
        # If refresh failed, suggest full re-authentication
        print("\n💡 Token refresh failed. You need to re-authenticate:")
        print("   python src/whoopy_auth_custom.py")
        return False
        
    else:
        # Token is still valid, test it anyway
        print("   ✅ Token is still valid")
        if test_token(credentials):
            print("✅ Token is working correctly!")
            return True
        else:
            print("❌ Token test failed despite being valid")
            print("💡 You may need to re-authenticate:")
            print("   python src/whoopy_auth_custom.py")
            return False

def get_token_status():
    """Get detailed token status"""
    print("📊 WHOOP Token Status")
    print("="*50)
    
    credentials = load_credentials()
    if not credentials:
        print("❌ No credentials found")
        return
    
    print("📋 Token Information:")
    print(f"   Token Type: {credentials.get('token_type', 'Unknown')}")
    print(f"   Scope: {credentials.get('scope', 'Unknown')}")
    
    if 'expires_at' in credentials:
        try:
            expires_at = datetime.fromisoformat(credentials['expires_at'])
            now = datetime.now()
            time_left = expires_at - now
            
            if time_left.total_seconds() > 0:
                print(f"   Expires: {expires_at}")
                print(f"   Time Left: {time_left}")
                print(f"   Status: {'✅ Valid' if time_left.total_seconds() > 300 else '⚠️  Expiring Soon'}")
            else:
                print(f"   Expired: {expires_at}")
                print(f"   Status: ❌ Expired")
        except:
            print("   Status: ⚠️  Could not determine expiration")
    
    if 'refresh_token' in credentials:
        print(f"   Refresh Token: ✅ Available")
    else:
        print(f"   Refresh Token: ❌ Not Available")
    
    if 'last_refreshed' in credentials:
        print(f"   Last Refreshed: {credentials['last_refreshed']}")
    
    # Test the token
    print("\n🧪 Testing token...")
    if test_token(credentials):
        print("✅ Token is working correctly!")
    else:
        print("❌ Token test failed")

def main():
    """Main function with options"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            get_token_status()
        elif command == "refresh":
            handle_token_refresh()
        elif command == "test":
            credentials = load_credentials()
            if credentials:
                test_token(credentials)
            else:
                print("❌ No credentials found")
        else:
            print("❌ Unknown command. Use: status, refresh, or test")
    else:
        # Default behavior: handle refresh
        handle_token_refresh()

if __name__ == "__main__":
    main() 
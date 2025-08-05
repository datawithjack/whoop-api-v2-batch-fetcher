import asyncio
import json
import os
import webbrowser
import requests
import pandas as pd
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

def load_users_from_csv(csv_file="users.csv"):
    """Load users from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} users from {csv_file}")
        
        # Check if email column exists
        if 'email' not in df.columns:
            print(f"❌ CSV must have 'email' column")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Convert to list of dictionaries
        users = []
        for index, row in df.iterrows():
            user = {
                'index': index + 1,
                'email': row['email'],
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'password': row.get('password', 'Not provided')
            }
            users.append(user)
        
        return users
        
    except FileNotFoundError:
        print(f"❌ CSV file '{csv_file}' not found")
        print("💡 Create a 'users.csv' file with columns: email, first_name, last_name, password")
        return None
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

def save_batch_credentials(all_credentials):
    """Save batch credentials to .whoop_credentials_batch.json"""
    with open(".whoop_credentials_batch.json", "w") as f:
        json.dump(all_credentials, f, indent=2)
    print("✅ Batch credentials saved to .whoop_credentials_batch.json")

def load_batch_credentials():
    """Load existing batch credentials"""
    try:
        with open(".whoop_credentials_batch.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"❌ Error loading batch credentials: {e}")
        return {}

async def authenticate_single_user(user, config, scopes):
    """Authenticate a single user following official WHOOP OAuth 2.0 flow"""
    print(f"\n🔐 Authenticating User {user['index']}: {user['email']}")
    print("-" * 60)
    
    # Step 1: Create authorization URL (following WHOOP docs)
    auth_url = "https://api.prod.whoop.com/oauth/oauth2/auth"
    auth_params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "scope": scopes,
        "state": f"batch_auth_{user['email']}_{user['index']}_{int(datetime.now().timestamp())}"
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(auth_params)}"
    
    print(f"📋 Opening browser for {user['email']}...")
    print(f"📋 Authorization URL: {auth_url_with_params}")
    print()
    print("📝 After authorization, you'll be redirected to your redirect URI")
    print("📝 Copy the entire URL from your browser and paste it below")
    print()
    
    # Open browser
    webbrowser.open(auth_url_with_params)
    
    # Step 2: Get authorization code from user
    print(f"📋 Paste the redirect URL for {user['email']}:")
    redirect_url = input().strip()
    
    # Parse the redirect URL to get the authorization code
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    # Check for errors
    if 'error' in query_params:
        error = query_params['error'][0]
        error_desc = query_params.get('error_description', [''])[0]
        print(f"❌ Authorization failed for {user['email']}: {error}")
        print(f"   Description: {error_desc}")
        if error == "invalid_scope":
            print("💡 This means your WHOOP app doesn't have permission for the requested scopes")
            print("💡 Contact WHOOP to add the required scopes to your app")
        return None
    
    # Get authorization code
    if 'code' not in query_params:
        print(f"❌ No authorization code found for {user['email']}")
        return None
    
    auth_code = query_params['code'][0]
    print(f"✅ Authorization code received for {user['email']}")
    
    # Step 3: Exchange authorization code for tokens (following WHOOP docs)
    print(f"🔄 Exchanging authorization code for {user['email']}...")
    
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
                print(f"⚠️  WARNING: No refresh token received for {user['email']}!")
                print("💡 This means your WHOOP app doesn't have the 'offline' scope")
                print("💡 Contact WHOOP to add the 'offline' scope to your app")
                print("💡 Without refresh tokens, you'll need to re-authenticate manually")
            
            # Get user profile
            profile_data = await get_user_profile(token_response.get('access_token'))
            
            # Create credentials object
            credentials = {
                "email": user['email'],
                "first_name": user.get('first_name', ''),
                "last_name": user.get('last_name', ''),
                "access_token": token_response.get('access_token'),
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "token_type": token_response.get('token_type', 'bearer'),
                "scope": token_response.get('scope', scopes),
                "auth_timestamp": datetime.now().isoformat(),
                "whoop_user_id": profile_data.get('user_id') if profile_data else None,
                "whoop_first_name": profile_data.get('first_name') if profile_data else None,
                "whoop_last_name": profile_data.get('last_name') if profile_data else None
            }
            
            print(f"✅ Token exchange successful for {user['email']}!")
            print(f"📅 Token expires at: {expires_at}")
            print(f"🆔 WHOOP User ID: {credentials['whoop_user_id']}")
            print(f"🔄 Refresh token: {'✅ Available' if refresh_token else '❌ Not Available'}")
            
            return credentials
            
        else:
            print(f"❌ Token exchange failed for {user['email']}: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during token exchange for {user['email']}: {e}")
        return None

async def get_user_profile(access_token):
    """Get user profile information"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://api.prod.whoop.com/developer/v2/user/profile/basic", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

async def refresh_user_token(user_email, refresh_token, config):
    """Refresh access token for a specific user (following WHOOP docs)"""
    print(f"🔄 Refreshing access token for {user_email}...")
    
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
            
            # Load existing batch credentials
            all_credentials = load_batch_credentials()
            
            # Update the specific user's credentials
            if user_email in all_credentials:
                all_credentials[user_email].update({
                    "access_token": token_response.get('access_token'),
                    "refresh_token": token_response.get('refresh_token', refresh_token),  # Use new refresh token if provided
                    "expires_in": expires_in,
                    "expires_at": expires_at.isoformat(),
                    "token_type": token_response.get('token_type', 'bearer'),
                    "scope": token_response.get('scope', 'offline'),
                    "auth_timestamp": datetime.now().isoformat()
                })
                
                # Save updated credentials
                save_batch_credentials(all_credentials)
                
                print(f"✅ Token refresh successful for {user_email}!")
                print(f"📅 New token expires at: {expires_at}")
                return True
            else:
                print(f"❌ User {user_email} not found in batch credentials")
                return False
            
        else:
            print(f"❌ Token refresh failed for {user_email}: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during token refresh for {user_email}: {e}")
        return False

async def test_batch_credentials(all_credentials):
    """Test all batch credentials"""
    print("\n🧪 Testing batch credentials...")
    print("="*60)
    
    successful_tests = 0
    failed_tests = 0
    
    for email, credentials in all_credentials.items():
        print(f"\n👤 Testing {email}...")
        
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Test user profile endpoint
        profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ {email}: API test successful!")
            print(f"   👤 WHOOP Name: {profile_data.get('first_name', 'Unknown')} {profile_data.get('last_name', 'Unknown')}")
            print(f"   🆔 WHOOP ID: {profile_data.get('user_id', 'Unknown')}")
            successful_tests += 1
        else:
            print(f"❌ {email}: API test failed - {response.status_code}")
            failed_tests += 1
    
    print(f"\n📊 Batch Test Summary:")
    print(f"✅ Successful: {successful_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    return successful_tests > 0

async def batch_authentication():
    """Main batch authentication function following official WHOOP OAuth 2.0"""
    print("🚀 WHOOP Batch Authentication (Official OAuth 2.0)")
    print("="*60)
    
    # Create configuration
    config = create_whoop_config()
    if not config:
        return False
    
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
    
    # Load users from CSV
    users = load_users_from_csv()
    if not users:
        return False
    
    # Load existing credentials
    existing_credentials = load_batch_credentials()
    
    print(f"📊 Found {len(existing_credentials)} existing authenticated users")
    print(f"📊 Found {len(users)} users in CSV")
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Authenticate all users (skip existing)")
    print("2. Re-authenticate all users (overwrite existing)")
    print("3. Authenticate specific users")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '4':
        print("👋 Goodbye!")
        return False
    
    # Process users based on choice
    all_credentials = existing_credentials.copy()
    newly_authenticated = 0
    
    if choice == '1':
        # Authenticate all users (skip existing)
        for user in users:
            if user['email'] in existing_credentials:
                print(f"⏭️  Skipping {user['email']} (already authenticated)")
                continue
            
            credentials = await authenticate_single_user(user, config, scope_string)
            if credentials:
                all_credentials[user['email']] = credentials
                newly_authenticated += 1
            else:
                print(f"❌ Failed to authenticate {user['email']}")
    
    elif choice == '2':
        # Re-authenticate all users
        for user in users:
            credentials = await authenticate_single_user(user, config, scope_string)
            if credentials:
                all_credentials[user['email']] = credentials
                newly_authenticated += 1
            else:
                print(f"❌ Failed to authenticate {user['email']}")
    
    elif choice == '3':
        # Authenticate specific users
        print("\nAvailable users:")
        for i, user in enumerate(users, 1):
            status = "✅" if user['email'] in existing_credentials else "❌"
            print(f"{i}. {status} {user['email']}")
        
        user_input = input("\nEnter user numbers to authenticate (comma-separated): ").strip()
        try:
            selected_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            selected_users = [users[i] for i in selected_indices if 0 <= i < len(users)]
            
            for user in selected_users:
                credentials = await authenticate_single_user(user, config, scope_string)
                if credentials:
                    all_credentials[user['email']] = credentials
                    newly_authenticated += 1
                else:
                    print(f"❌ Failed to authenticate {user['email']}")
        except:
            print("❌ Invalid selection")
            return False
    
    else:
        print("❌ Invalid option")
        return False
    
    # Save all credentials
    if newly_authenticated > 0:
        save_batch_credentials(all_credentials)
        print(f"\n✅ Successfully authenticated {newly_authenticated} new users")
        print(f"📊 Total authenticated users: {len(all_credentials)}")
        
        # Test credentials
        await test_batch_credentials(all_credentials)
        
        return True
    else:
        print("\n⚠️  No new users were authenticated")
        return False

def list_batch_users():
    """List all batch authenticated users"""
    credentials = load_batch_credentials()
    
    if not credentials:
        print("📭 No batch authenticated users found")
        return
    
    print(f"\n👥 Batch Authenticated Users ({len(credentials)}):")
    print("="*80)
    
    for email, user_data in credentials.items():
        print(f"📧 {email}")
        print(f"   👤 Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
        print(f"   🆔 WHOOP ID: {user_data.get('whoop_user_id', 'Not available')}")
        print(f"   📅 Authenticated: {user_data.get('auth_timestamp', 'Unknown')}")
        
        # Check if token is expired
        if 'expires_at' in user_data:
            try:
                expires_at = datetime.fromisoformat(user_data['expires_at'])
                if datetime.now() > expires_at:
                    print(f"   ⚠️  Token: EXPIRED")
                else:
                    time_left = expires_at - datetime.now()
                    print(f"   ✅ Token: Valid ({time_left})")
            except:
                print(f"   ⚠️  Token: Unknown status")
        
        # Check refresh token
        has_refresh = user_data.get('refresh_token') is not None
        print(f"   🔄 Refresh Token: {'✅ Available' if has_refresh else '❌ Not Available'}")
        print()

def main():
    """Main function"""
    print("🚀 WHOOP Batch Authentication Setup (Official OAuth 2.0)")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Start batch authentication")
        print("2. List authenticated users")
        print("3. Test batch credentials")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            success = asyncio.run(batch_authentication())
            if success:
                print("\n🎉 Batch authentication complete!")
                print("💡 You can now use the batch credentials for data fetching")
        
        elif choice == '2':
            list_batch_users()
        
        elif choice == '3':
            credentials = load_batch_credentials()
            if credentials:
                asyncio.run(test_batch_credentials(credentials))
            else:
                print("❌ No batch credentials found")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 
import json
import csv
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def ensure_exports_directory():
    """Ensure the exports directory and subdirectories exist"""
    exports_dir = "exports"
    json_dir = os.path.join(exports_dir, "json")
    csv_dir = os.path.join(exports_dir, "combined_csv")
    
    # Create main exports directory
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
        print(f"Created exports directory: {exports_dir}")
    
    # Create json subdirectory
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
        print(f"Created json directory: {json_dir}")
    
    # Create combined_csv subdirectory
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
        print(f"Created combined_csv directory: {csv_dir}")
    
    return exports_dir

def load_batch_credentials():
    """Load saved batch credentials"""
    try:
        with open(".whoop_credentials_batch.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No batch credentials file found. Please run batch authentication first:")
        print("   python src/batch_whoopy_auth.py")
        return None
    except Exception as e:
        print(f"❌ Error loading batch credentials: {e}")
        return None

def save_batch_credentials(credentials_dict):
    """Save updated batch credentials"""
    try:
        with open(".whoop_credentials_batch.json", "w") as f:
            json.dump(credentials_dict, f, indent=2)
        print("✅ Batch credentials updated")
    except Exception as e:
        print(f"❌ Error saving batch credentials: {e}")

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

def refresh_user_token_batch(credentials):
    """Refresh access token for batch users using the same logic as token_refresh_handler"""
    print("  🔄 Refreshing access token...")
    
    if 'refresh_token' not in credentials:
        print("  ❌ No refresh token available")
        return False
    
    # Get environment variables
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    redirect_uri = os.getenv('WHOOP_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        print("  ❌ Missing environment variables for token refresh")
        return False
    
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
            
            print("  ✅ Token refreshed successfully!")
            print(f"  📅 New expiration: {expires_at}")
            return True
            
        else:
            print(f"  ❌ Token refresh failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error details: {error_data}")
            except:
                print(f"  Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception during token refresh: {e}")
        return False

def test_user_token(credentials):
    """Test if user token is valid"""
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
    
    try:
        response = requests.get(profile_url, headers=headers)
        return response.status_code == 200
    except:
        return False

def check_token_validity(credentials):
    """Check if token is still valid without refreshing"""
    if not credentials.get('access_token'):
        return False
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
    
    try:
        response = requests.get(profile_url, headers=headers)
        return response.status_code == 200
    except:
        return False

def flatten_sleep_record(record):
    """Flatten a sleep record for CSV export with expanded nested fields"""
    flat_record = {}
    
    for key, value in record.items():
        if isinstance(value, dict):
            # Special handling for score_sleep_needed and score_stage_summary
            if key in ['score_sleep_needed', 'score_stage_summary']:
                # Expand these nested dictionaries into individual columns
                for nested_key, nested_value in value.items():
                    flat_record[f"{key}.{nested_key}"] = nested_value
            else:
                # For other nested dictionaries, use the original flattening
                for nested_key, nested_value in value.items():
                    flat_record[f"{key}_{nested_key}"] = nested_value
        elif isinstance(value, list):
            # Convert lists to JSON strings
            flat_record[key] = json.dumps(value)
        else:
            flat_record[key] = value
    
    return flat_record

def export_sleep_data_to_csv(sleep_records, exports_dir, user_email="user", start_date=None, end_date=None):
    """Export sleep data to CSV files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not sleep_records:
        print("  ⚠️  No sleep records to export")
        return None
    
    # Flatten all records
    flattened_records = []
    for record in sleep_records:
        flat_record = flatten_sleep_record(record)
        flat_record['user_email'] = user_email
        flattened_records.append(flat_record)
    
    # Create user-specific filename with date range
    safe_user_id = user_email.replace('@', '_at_').replace('.', '_')
    if start_date and end_date:
        date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        user_filename = os.path.join(exports_dir, f"sleep_data_batch_{safe_user_id}_{date_range}_{timestamp}.csv")
    else:
        user_filename = os.path.join(exports_dir, f"sleep_data_batch_{safe_user_id}_{timestamp}.csv")
    
    # Get all field names
    fieldnames = set()
    for record in flattened_records:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))
    
    # Write CSV
    with open(user_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_records)
    
    print(f"  ✅ User CSV exported: {user_filename} ({len(flattened_records)} records)")
    return user_filename

def get_date_range_from_user():
    """Get start and end dates from user input"""
    print("\n📅 Date Range Selection")
    print("="*40)
    print("Enter the date range for sleep data extraction")
    print("Format: YYYY-MM-DD (e.g., 2024-01-01)")
    print()
    
    while True:
        try:
            start_date_str = input("Enter start date (YYYY-MM-DD): ").strip()
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            
            end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Validate date range
            if start_date > end_date:
                print("❌ Start date cannot be after end date. Please try again.")
                continue
            
            if end_date > datetime.now():
                print("❌ End date cannot be in the future. Please try again.")
                continue
            
            print(f"✅ Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            return start_date, end_date
            
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD format.")
        except Exception as e:
            print(f"❌ Error: {e}")

def fetch_user_sleep_data(credentials, start_date=None, end_date=None, days_back=30):
    """Fetch sleep data for a specific user"""
    if start_date and end_date:
        print(f"  😴 Fetching sleep data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    else:
        print(f"  😴 Fetching sleep data for last {days_back} days...")
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
    
    print(f"  📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    # WHOOP v2 sleep endpoint
    sleep_url = "https://api.prod.whoop.com/developer/v2/activity/sleep"
    
    all_sleep_records = []
    next_token = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"    📄 Fetching page {page_count}...")
        
        # Prepare parameters
        params = {
            'start': start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'end': end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'limit': 25  # WHOOP API limit
        }
        
        if next_token:
            params['nextToken'] = next_token
        
        try:
            response = requests.get(sleep_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract records
                records = data.get('records', [])
                if records:
                    all_sleep_records.extend(records)
                    print(f"      ✅ Retrieved {len(records)} sleep records")
                    
                    # Check for next page
                    next_token = data.get('next_token')
                    if not next_token:
                        print(f"      📄 No more pages available")
                        break
                else:
                    print(f"      📄 No records found in response")
                    break
                    
            elif response.status_code == 401:
                print(f"      ❌ 401: Unauthorized - Token may be expired")
                return None
                
            elif response.status_code == 403:
                print(f"      ❌ 403: Forbidden - Check app permissions")
                return None
                
            elif response.status_code == 429:
                print(f"      ❌ 429: Rate Limited - Waiting 60 seconds...")
                import time
                time.sleep(60)
                continue
                
            else:
                print(f"      ❌ {response.status_code}: Unexpected status")
                try:
                    error_data = response.json()
                    print(f"      Error details: {error_data}")
                except:
                    print(f"      Raw response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            return None
    
    print(f"    ✅ Total sleep records: {len(all_sleep_records)}")
    return all_sleep_records

def get_user_profile(credentials):
    """Get user profile information"""
    print("  👤 Fetching user profile...")
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
    
    try:
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"  ✅ Profile retrieved: {profile_data.get('first_name', 'Unknown')} {profile_data.get('last_name', 'Unknown')}")
            return profile_data
        else:
            print(f"  ❌ Profile fetch failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error fetching profile: {e}")
        return None

def process_user(user_email, user_credentials, exports_dir, start_date=None, end_date=None, days_back=30):
    """Process a single user's sleep data"""
    print(f"\n👤 Processing user: {user_email}")
    print("-" * 50)
    
    # First check if current token is still valid
    if check_token_validity(user_credentials):
        print("  ✅ Current token is still valid!")
    elif is_token_expired(user_credentials):
        print("  ❌ Token has expired. Attempting automatic refresh...")
        
        # Use our batch-compatible token refresh function
        if refresh_user_token_batch(user_credentials):
            # Test the refreshed token
            if test_user_token(user_credentials):
                print("  ✅ Token refreshed successfully!")
            else:
                print("  ❌ Refreshed token failed test.")
                print("  💡 You may need to re-authenticate this user manually:")
                print(f"     python src/reauthenticate_user.py")
                print("  ⏭️  Skipping user for now.")
                return False
        else:
            print("  ❌ Token refresh failed.")
            print("  💡 You may need to re-authenticate this user manually:")
            print(f"     python src/reauthenticate_user.py")
            print("  ⏭️  Skipping user for now.")
            return False
    else:
        time_left = datetime.fromisoformat(user_credentials['expires_at']) - datetime.now()
        print(f"  ✅ Token valid for: {time_left}")
    
    # Get user profile
    profile = get_user_profile(user_credentials)
    if not profile:
        print("  ❌ Could not fetch user profile. Skipping user.")
        return False
    
    # Update user info in credentials
    user_credentials.update({
        'first_name': profile.get('first_name', ''),
        'last_name': profile.get('last_name', ''),
        'whoop_user_id': profile.get('user_id', ''),
        'whoop_first_name': profile.get('first_name', ''),
        'whoop_last_name': profile.get('last_name', '')
    })
    
    user_name = f"{profile.get('first_name', 'Unknown')} {profile.get('last_name', 'Unknown')}"
    whoop_user_id = profile.get('user_id', 'Unknown')
    
    # Fetch sleep data
    sleep_records = fetch_user_sleep_data(user_credentials, start_date, end_date, days_back)
    
    if sleep_records:
        # Export to CSV
        csv_filename = export_sleep_data_to_csv(sleep_records, exports_dir, user_email, start_date, end_date)
        
        # Save to JSON as well
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_user_id = user_email.replace('@', '_at_').replace('.', '_')
        if start_date and end_date:
            date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            json_filename = os.path.join(exports_dir, "json", f"sleep_data_batch_{safe_user_id}_{date_range}_{timestamp}.json")
        else:
            json_filename = os.path.join(exports_dir, "json", f"sleep_data_batch_{safe_user_id}_{timestamp}.json")
        
        json_data = {
            'user_info': {
                'email': user_email,
                'whoop_user_id': whoop_user_id,
                'name': user_name
            },
            'fetch_info': {
                'timestamp': datetime.now().isoformat(),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_records': len(sleep_records)
            },
            'sleep_records': sleep_records
        }
        
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"  ✅ JSON data saved: {json_filename}")
        
        # Basic analysis
        print(f"  📈 Basic Analysis:")
        
        # Calculate average sleep duration
        total_duration = 0
        total_score = 0
        valid_scores = 0
        
        for record in sleep_records:
            # Calculate sleep score
            if 'score' in record and record['score']:
                score = record['score'].get('sleep_performance_percentage')
                if score is not None:
                    total_score += score
                    valid_scores += 1
            
            # Calculate duration from start/end times
            if 'start' in record and 'end' in record:
                try:
                    start_time = datetime.fromisoformat(record['start'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(record['end'].replace('Z', '+00:00'))
                    duration = (end_time - start_time).total_seconds() / 3600
                    total_duration += duration
                except:
                    pass
        
        if len(sleep_records) > 0:
            avg_duration = total_duration / len(sleep_records)
            print(f"    Average sleep duration: {avg_duration:.2f} hours")
        
        if valid_scores > 0:
            avg_score = total_score / valid_scores
            print(f"    Average sleep score: {avg_score:.1f}%")
        
        return True
    else:
        print("  ❌ No sleep data retrieved")
        return False

def main():
    """Main function to fetch sleep data for all users in batch"""
    print("🔄 Batch WHOOP Sleep Data Fetcher")
    print("="*60)
    
    # Create exports directory
    exports_dir = ensure_exports_directory()
    
    # Load batch credentials
    batch_credentials = load_batch_credentials()
    if not batch_credentials:
        return
    
    print(f"📋 Found {len(batch_credentials)} users to process")
    
    # Get date range from user
    start_date, end_date = get_date_range_from_user()
    
    # Track results
    successful_users = []
    failed_users = []
    updated_credentials = {}
    
    # Process each user
    for user_email, user_credentials in batch_credentials.items():
        try:
            # Process the user
            success = process_user(user_email, user_credentials, exports_dir, start_date, end_date)
            
            if success:
                successful_users.append(user_email)
                # Store updated credentials
                updated_credentials[user_email] = user_credentials
            else:
                failed_users.append(user_email)
                # Keep original credentials for failed users
                updated_credentials[user_email] = user_credentials
                
        except Exception as e:
            print(f"  ❌ Unexpected error processing {user_email}: {e}")
            failed_users.append(user_email)
            updated_credentials[user_email] = user_credentials
        
        # Add delay between users to avoid rate limiting
        if len(batch_credentials) > 1:
            print("  ⏳ Waiting 5 seconds before next user...")
            import time
            time.sleep(5)
    
    # Save updated credentials
    save_batch_credentials(updated_credentials)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 BATCH SUMMARY")
    print("="*60)
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"✅ Successful users: {len(successful_users)}")
    print(f"❌ Failed users: {len(failed_users)}")
    print(f"📁 Exports directory: {exports_dir}")
    
    if successful_users:
        print(f"\n✅ Successfully processed:")
        for user in successful_users:
            print(f"  • {user}")
    
    if failed_users:
        print(f"\n❌ Failed to process:")
        for user in failed_users:
            print(f"  • {user}")
    
    print(f"\n📁 Check the 'exports' directory for CSV files")
    print(f"📁 Check the root directory for JSON files")

if __name__ == "__main__":
    main() 
import json
import csv
import os
import requests
import glob
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    return data_dir

def load_batch_credentials():
    """Load saved batch credentials from GitHub Secrets environment variable"""
    try:
        credentials_json = os.getenv('WHOOP_BATCH_CREDENTIALS')
        if not credentials_json:
            print("❌ WHOOP_BATCH_CREDENTIALS environment variable not set")
            print("💡 Please set this secret in GitHub repository settings")
            return None
        return json.loads(credentials_json)
    except Exception as e:
        print(f"❌ Error loading batch credentials: {e}")
        return None

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
            print("  ⚠️  Manual update needed: Update WHOOP_BATCH_CREDENTIALS in GitHub Secrets")
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

def find_user_csv_file(user_email):
    """Find the CSV file for a specific user in the data directory"""
    data_dir = "data"
    filename = f"sleep_data_batch_{user_email.replace('@', '_at_').replace('.', '_')}.csv"
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        return filepath
    else:
        # Return the path even if file doesn't exist (will be created)
        return filepath

def get_latest_date_from_csv(csv_file):
    """Get the latest date from a CSV file"""
    if not os.path.exists(csv_file):
        return None
    
    latest_date = None
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if 'start' in row and row['start']:
                    try:
                        # Parse the start date (ISO format)
                        date_str = row['start'].replace('Z', '+00:00')
                        record_date = datetime.fromisoformat(date_str)
                        
                        if latest_date is None or record_date > latest_date:
                            latest_date = record_date
                    except:
                        continue
                        
    except Exception as e:
        print(f"  ❌ Error reading CSV file: {e}")
        return None
    
    return latest_date

def flatten_sleep_record(record):
    """Flatten a sleep record for CSV export with expanded nested fields"""
    flat_record = {}
    
    # Basic fields
    for key, value in record.items():
        if key == 'score' and isinstance(value, dict):
            # Expand score fields
            for score_key, score_value in value.items():
                if isinstance(score_value, dict):
                    # Convert nested dict to string representation
                    flat_record[f'score_{score_key}'] = str(score_value)
                else:
                    flat_record[f'score_{score_key}'] = score_value
        else:
            flat_record[key] = value
    
    return flat_record

def fetch_new_sleep_data(credentials, start_date, days_back=7):
    """Fetch new sleep data from WHOOP API"""
    print(f"  📅 Fetching data from {start_date.strftime('%Y-%m-%d')} onwards...")
    
    # WHOOP API endpoint
    endpoint = "https://api.prod.whoop.com/developer/v2/activity/sleep"
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    # Calculate date range
    end_date = datetime.now()
    if start_date:
        # Set start_date to beginning of next day to avoid duplicate records
        start_date = (start_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # If no start date, fetch last 7 days
        start_date = end_date - timedelta(days=days_back)
    
    # Format dates for API (milliseconds format required by WHOOP API)
    start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
    end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
    
    params = {
        'start': start_str,
        'end': end_str,
        'limit': 25  # Maximum limit per page
    }
    
    all_records = []
    next_token = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"    📄 Fetching page {page_count}...")
        
        current_params = params.copy()
        if next_token:
            current_params['nextToken'] = next_token
            
        try:
            response = requests.get(endpoint, headers=headers, params=current_params)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                
                if records:
                    all_records.extend(records)
                    print(f"      ✅ Retrieved {len(records)} records")
                    
                    next_token = data.get('next_token')
                    if not next_token:
                        print(f"      📄 No more pages available")
                        break
                else:
                    print(f"      📄 No records found in response")
                    break
                    
            elif response.status_code == 401:
                print("      ❌ 401: Unauthorized - Token may be expired")
                return None
            elif response.status_code == 403:
                print("      ❌ 403: Forbidden - Check app permissions")
                return None
            elif response.status_code == 429:
                print("      ❌ 429: Rate Limited - Waiting 60 seconds...")
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
                print(f"      Request params: {current_params}")
                return None
                
        except Exception as e:
            print(f"      ❌ Request failed: {e}")
            return None
    
    print(f"  ✅ Total new records fetched: {len(all_records)}")
    return all_records

def append_to_csv(csv_file, new_records, user_email):
    """Append new records to existing CSV file"""
    if not new_records:
        print("  ⚠️  No new records to append")
        return
    
    # Read existing fieldnames
    existing_fieldnames = []
    if os.path.exists(csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_fieldnames = reader.fieldnames
    
    # Flatten new records
    flattened_records = []
    for record in new_records:
        flat_record = flatten_sleep_record(record)
        flat_record['user_email'] = user_email
        flattened_records.append(flat_record)
    
    # Get all field names (existing + new)
    all_fieldnames = set(existing_fieldnames) if existing_fieldnames else set()
    for record in flattened_records:
        all_fieldnames.update(record.keys())
    all_fieldnames = sorted(list(all_fieldnames))
    
    # Append to CSV
    mode = 'a' if os.path.exists(csv_file) else 'w'
    with open(csv_file, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
        
        # Write header only if creating new file
        if mode == 'w':
            writer.writeheader()
        
        # Write new records
        for record in flattened_records:
            # Ensure all fields are present
            row = {field: record.get(field, '') for field in all_fieldnames}
            writer.writerow(row)
    
    print(f"  ✅ Appended {len(flattened_records)} new records to {csv_file}")

def update_user_sleep_data(user_email, user_credentials):
    """Update sleep data for a single user"""
    print(f"\n🔄 Processing user: {user_email}")
    
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
                print("  💡 You may need to re-authenticate this user manually")
                print("  ⏭️  Skipping user for now.")
                return False
        else:
            print("  ❌ Token refresh failed.")
            print("  💡 You may need to re-authenticate this user manually")
            print("  ⏭️  Skipping user for now.")
            return False
    else:
        time_left = datetime.fromisoformat(user_credentials['expires_at']) - datetime.now()
        print(f"  ✅ Token valid for: {time_left}")
    
    # Find existing CSV file
    csv_file = find_user_csv_file(user_email)
    print(f"  📁 Using file: {csv_file}")
    
    # Get latest date from CSV
    latest_date = get_latest_date_from_csv(csv_file)
    if latest_date:
        print(f"  📅 Latest date in CSV: {latest_date.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  ⚠️  Could not determine latest date from CSV")
        latest_date = None
    
    # Fetch new data
    new_records = fetch_new_sleep_data(user_credentials, latest_date)
    if new_records is None:
        print("  ❌ Failed to fetch new data")
        return False
    
    # Append new records to CSV
    append_to_csv(csv_file, new_records, user_email)
    
    return True

def main():
    """Main function to update sleep data for all batch users"""
    print("🔄 WHOOP Sleep Data Updater (GitHub Actions)")
    print("=" * 50)
    
    # Ensure data directory exists
    data_dir = ensure_data_directory()
    
    # Load batch credentials from environment
    batch_credentials = load_batch_credentials()
    if not batch_credentials:
        return
    
    print(f"📋 Found {len(batch_credentials)} users in batch credentials")
    
    # Track results
    successful_users = []
    failed_users = []
    
    # Process each user
    for user_email, user_credentials in batch_credentials.items():
        try:
            # Process the user
            success = update_user_sleep_data(user_email, user_credentials)
            
            if success:
                successful_users.append(user_email)
            else:
                failed_users.append(user_email)
                
        except Exception as e:
            print(f"  ❌ Unexpected error processing {user_email}: {e}")
            failed_users.append(user_email)
        
        # Add delay between users to avoid rate limiting
        if len(batch_credentials) > 1:
            print("  ⏳ Waiting 5 seconds before next user...")
            import time
            time.sleep(5)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Update complete: {len(successful_users)}/{len(batch_credentials)} users processed successfully")
    
    if failed_users:
        print("⚠️  Some users failed to update. Check the logs above for details.")
        print("💡 Failed users may need manual re-authentication:")
        for user in failed_users:
            print(f"   • {user}")

if __name__ == "__main__":
    main()

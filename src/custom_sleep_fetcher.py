import json
import csv
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def ensure_exports_directory():
    """Ensure the exports directory exists"""
    exports_dir = "exports"
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
        print(f"Created exports directory: {exports_dir}")
    return exports_dir

def load_credentials():
    """Load saved credentials"""
    try:
        with open(".whoop_credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No credentials file found. Please run authentication first:")
        print("   python src/whoopy_auth_custom.py")
        return None
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def flatten_sleep_record(record):
    """Flatten a sleep record for CSV export"""
    flat_record = {}
    
    for key, value in record.items():
        if isinstance(value, dict):
            # Flatten nested dictionaries
            for nested_key, nested_value in value.items():
                flat_record[f"{key}_{nested_key}"] = nested_value
        elif isinstance(value, list):
            # Convert lists to JSON strings
            flat_record[key] = json.dumps(value)
        else:
            flat_record[key] = value
    
    return flat_record

def export_sleep_data_to_csv(sleep_records, exports_dir, user_email="user"):
    """Export sleep data to CSV files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not sleep_records:
        print("⚠️  No sleep records to export")
        return None
    
    # Flatten all records
    flattened_records = []
    for record in sleep_records:
        flat_record = flatten_sleep_record(record)
        flat_record['user_email'] = user_email
        flattened_records.append(flat_record)
    
    # Create user-specific filename
    safe_user_id = user_email.replace('@', '_at_').replace('.', '_')
    user_filename = os.path.join(exports_dir, f"sleep_data_custom_{safe_user_id}_{timestamp}.csv")
    
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
    
    print(f"✅ User CSV exported: {user_filename} ({len(flattened_records)} records)")
    return user_filename

def fetch_sleep_data(credentials, days_back=30):
    """Fetch sleep data using custom authentication"""
    print(f"😴 Fetching sleep data for last {days_back} days...")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
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
        print(f"  📄 Fetching page {page_count}...")
        
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
                    print(f"    ✅ Retrieved {len(records)} sleep records")
                    
                    # Check for next page
                    next_token = data.get('next_token')
                    if not next_token:
                        print(f"    📄 No more pages available")
                        break
                else:
                    print(f"    📄 No records found in response")
                    break
                    
            elif response.status_code == 401:
                print(f"    ❌ 401: Unauthorized - Token may be expired")
                print(f"    💡 Run: python src/whoopy_auth_custom.py")
                break
                
            elif response.status_code == 403:
                print(f"    ❌ 403: Forbidden - Check app permissions")
                break
                
            elif response.status_code == 429:
                print(f"    ❌ 429: Rate Limited - Waiting 60 seconds...")
                import time
                time.sleep(60)
                continue
                
            else:
                print(f"    ❌ {response.status_code}: Unexpected status")
                try:
                    error_data = response.json()
                    print(f"    Error details: {error_data}")
                except:
                    print(f"    Raw response: {response.text[:200]}")
                break
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            break
    
    print(f"  ✅ Total sleep records: {len(all_sleep_records)}")
    return all_sleep_records

def get_user_profile(credentials):
    """Get user profile information"""
    print("👤 Fetching user profile...")
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json"
    }
    
    profile_url = "https://api.prod.whoop.com/developer/v2/user/profile/basic"
    
    try:
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ Profile retrieved: {profile_data.get('first_name', 'Unknown')} {profile_data.get('last_name', 'Unknown')}")
            return profile_data
        else:
            print(f"❌ Profile fetch failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return None

def main():
    """Main function to fetch sleep data using custom authentication"""
    print("🔄 Custom WHOOP Sleep Data Fetcher")
    print("="*60)
    
    # Create exports directory
    exports_dir = ensure_exports_directory()
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return
    
    # Check token expiration and handle refresh
    if 'expires_at' in credentials:
        try:
            expires_at = datetime.fromisoformat(credentials['expires_at'])
            if datetime.now() > expires_at:
                print("❌ Token has expired. Attempting automatic refresh...")
                
                # Import and use token refresh handler
                try:
                    from token_refresh_handler import refresh_access_token, test_token
                    
                    if refresh_access_token(credentials):
                        # Reload credentials after refresh
                        credentials = load_credentials()
                        if test_token(credentials):
                            print("✅ Token refreshed successfully!")
                        else:
                            print("❌ Refreshed token failed test. Please re-authenticate:")
                            print("   python src/whoopy_auth_custom.py")
                            return
                    else:
                        print("❌ Token refresh failed. Please re-authenticate:")
                        print("   python src/whoopy_auth_custom.py")
                        return
                        
                except ImportError:
                    print("❌ Token refresh handler not available. Please re-authenticate:")
                    print("   python src/whoopy_auth_custom.py")
                    return
                    
            else:
                time_left = expires_at - datetime.now()
                print(f"✅ Token valid for: {time_left}")
        except:
            print("⚠️  Could not check token expiration")
    
    # Get user profile
    profile = get_user_profile(credentials)
    if not profile:
        return
    
    user_email = profile.get('email', 'authenticated_user')
    user_name = f"{profile.get('first_name', 'Unknown')} {profile.get('last_name', 'Unknown')}"
    whoop_user_id = profile.get('user_id', 'Unknown')
    
    # Fetch sleep data
    sleep_records = fetch_sleep_data(credentials, days_back=30)
    
    if sleep_records:
        # Export to CSV
        csv_filename = export_sleep_data_to_csv(sleep_records, exports_dir, user_email)
        
        # Save to JSON as well
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"sleep_data_custom_{timestamp}.json"
        
        json_data = {
            'user_info': {
                'email': user_email,
                'whoop_user_id': whoop_user_id,
                'name': user_name
            },
            'fetch_info': {
                'timestamp': datetime.now().isoformat(),
                'total_records': len(sleep_records)
            },
            'sleep_records': sleep_records
        }
        
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"✅ JSON data saved: {json_filename}")
        
        # Create summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"👤 User: {user_name} ({user_email})")
        print(f"🆔 WHOOP ID: {whoop_user_id}")
        print(f"😴 Sleep records: {len(sleep_records)}")
        print(f"📁 CSV file: {csv_filename}")
        print(f"📁 JSON file: {json_filename}")
        
        # Basic analysis
        if sleep_records:
            print(f"\n📈 Basic Analysis:")
            
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
                print(f"   Average sleep duration: {avg_duration:.2f} hours")
            
            if valid_scores > 0:
                avg_score = total_score / valid_scores
                print(f"   Average sleep score: {avg_score:.1f}%")
    
    else:
        print("❌ No sleep data retrieved")

if __name__ == "__main__":
    main() 
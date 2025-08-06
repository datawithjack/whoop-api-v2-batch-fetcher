# WHOOP API V2 - Development Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- WHOOP API credentials (Client ID, Client Secret)
- Access to WHOOP Developer Portal

### Initial Setup
```bash
# 1. Clone or navigate to project directory
cd WHOOP_API_V2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create environment file
cp .env.example .env
# Edit .env with your credentials
```

## 🔐 Authentication Setup

### Single User Authentication
```bash
# Run simple authentication
python src/whoop_authenication_simple.py

# Follow the prompts:
# 1. Enter your email
# 2. Open the generated URL in browser
# 3. Authorize the application
# 4. Copy the authorization code
# 5. Paste the code when prompted
```

### Batch User Authentication
```bash
# 1. Prepare users.csv file
echo "email,first_name,last_name" > users.csv
echo "user1@example.com,John,Doe" >> users.csv
echo "user2@example.com,Jane,Smith" >> users.csv

# 2. Run batch authentication
python src/whoop_authenication_batch.py

# 3. Follow the prompts for each user
```

### Verify Authentication
```python
import pickle

# Check stored tokens
with open("whoop_user_tokens.pkl", 'rb') as f:
    tokens = pickle.load(f)

print(f"Authenticated users: {len(tokens)}")
for user_id, token_info in tokens.items():
    print(f"- {user_id}: {token_info.get('whoop_user_id', 'Unknown')}")
```

## 📊 Data Fetching

### Fetch Sleep Data
```bash
# Fetch sleep data for all authenticated users
python Scripts/fetch_sleep_data_v2.py
```

### Custom Date Range
```python
# Modify the date range in fetch_sleep_data_v2.py
start_date = end_date - timedelta(days=7)  # Last 7 days
# or
start_date = datetime(2024, 8, 1)  # Specific start date
```

### Monitor Progress
The script provides real-time feedback:
```
Loaded tokens for 2 users
Fetching sleep data from: https://api.prod.whoop.com/developer/v2/activity/sleep
Date range: 2024-08-01T00:00:00.000000Z to 2024-08-31T23:59:59.999999Z
Limit: 25 records per request
================================================================================

Processing user: user@example.com
WHOOP User ID: 12345678
  Fetching page 1...
    Retrieved 25 sleep records
  Fetching page 2...
    Retrieved 15 sleep records
    No more pages available
  ✅ Total sleep records for user user@example.com: 40
```

## 🧪 Testing

### Test Endpoints
```bash
# Test sleep endpoint functionality
python src/whoop_sleep_end_point_tester.py
```

### Validate Responses
```python
# Add validation to your scripts
def validate_sleep_response(response):
    if response.status_code != 200:
        return False
    
    data = response.json()
    if 'records' not in data:
        return False
    
    return True
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add to any script for detailed output
```

## 🔧 Common Development Tasks

### Adding New Endpoints

1. **Create endpoint function**:
```python
def fetch_workout_data(access_token, start_date, end_date):
    """Fetch workout data from WHOOP API"""
    endpoint = "https://api.prod.whoop.com/developer/v2/activity/workout"
    
    params = {
        'start': start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'end': end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'limit': 25
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None
```

2. **Add to main script**:
```python
def fetch_all_workout_data():
    """Fetch workout data for all users"""
    tokens = load_tokens()
    all_workout_data = {}
    
    for user_id, token_info in tokens.items():
        workout_data = fetch_workout_data(
            token_info['access_token'],
            start_date,
            end_date
        )
        all_workout_data[user_id] = workout_data
    
    return all_workout_data
```

### Error Handling

1. **Add comprehensive error handling**:
```python
def safe_api_call(endpoint, access_token, params=None):
    """Make API call with error handling"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Token expired - re-authenticate")
            return None
        elif response.status_code == 429:
            print("Rate limited - waiting...")
            time.sleep(60)
            return safe_api_call(endpoint, access_token, params)
        else:
            print(f"API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None
```

### Data Analysis

1. **Create analysis functions**:
```python
def analyze_workout_data(workout_data):
    """Analyze workout patterns"""
    total_workouts = len(workout_data.get('records', []))
    total_duration = sum(
        record.get('duration', 0) 
        for record in workout_data.get('records', [])
    )
    
    return {
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'avg_duration': total_duration / total_workouts if total_workouts > 0 else 0
    }
```

## 📈 Performance Optimization

### Rate Limiting
```python
# Add delays between requests
import time

def fetch_with_rate_limit(endpoint, access_token, params):
    """Fetch data with rate limiting"""
    response = make_api_request(endpoint, access_token, params)
    
    # Add delay between requests
    time.sleep(1)  # 1 second delay
    
    return response
```

### Batch Processing
```python
# Process users in batches
def process_users_in_batches(users, batch_size=5):
    """Process users in smaller batches"""
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        
        for user in batch:
            process_user(user)
        
        # Delay between batches
        time.sleep(5)
```

### Caching
```python
# Implement simple caching
import json
from datetime import datetime, timedelta

def get_cached_data(key, max_age_hours=24):
    """Get cached data if not expired"""
    cache_file = f"cache_{key}.json"
    
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        cache_time = datetime.fromisoformat(cached['timestamp'])
        if datetime.now() - cache_time < timedelta(hours=max_age_hours):
            return cached['data']
    except:
        pass
    
    return None

def cache_data(key, data):
    """Cache data with timestamp"""
    cache_file = f"cache_{key}.json"
    
    with open(cache_file, 'w') as f:
        json.dump({
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, f)
```

## 🔍 Debugging

### Common Issues

1. **Token Expiration**:
```python
# Check token expiration
def is_token_expired(token_info):
    if 'expires_at' not in token_info:
        return False
    
    return datetime.now() > token_info['expires_at']
```

2. **Rate Limiting**:
```python
# Handle rate limiting
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    print(f"Rate limited - waiting {retry_after} seconds")
    time.sleep(retry_after)
```

3. **Invalid Parameters**:
```python
# Validate parameters
def validate_date_range(start_date, end_date):
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")
    
    if end_date > datetime.now():
        raise ValueError("End date cannot be in the future")
```

### Debug Tools

1. **Request Logging**:
```python
import logging

# Set up request logging
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

2. **Response Inspection**:
```python
def inspect_response(response):
    """Inspect API response for debugging"""
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content: {response.text[:500]}...")
```

## 📝 Best Practices

### Code Organization
1. **Separate concerns**: Keep authentication, data fetching, and analysis separate
2. **Use functions**: Break code into reusable functions
3. **Add documentation**: Include docstrings for all functions
4. **Handle errors**: Implement comprehensive error handling

### Data Management
1. **Validate data**: Check response structure before processing
2. **Backup data**: Keep copies of important data
3. **Use timestamps**: Include timestamps in filenames
4. **Clean up**: Remove old cache files periodically

### API Usage
1. **Respect limits**: Follow rate limiting guidelines
2. **Handle pagination**: Always implement pagination for large datasets
3. **Validate tokens**: Check token validity before requests
4. **Log activity**: Keep logs of API usage

## 🚀 Deployment

### Production Considerations
1. **Environment variables**: Use .env files for configuration
2. **Error monitoring**: Implement proper error logging
3. **Scheduling**: Use cron jobs for regular data fetching
4. **Backup**: Implement data backup strategies

### Monitoring
```python
# Add monitoring to your scripts
def log_api_usage(endpoint, user_id, status_code, response_time):
    """Log API usage for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'user_id': user_id,
        'status_code': status_code,
        'response_time': response_time
    }
    
    with open('api_usage.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

---

**Last Updated**: August 2024  
**Development Status**: Active  
**Best Practices**: Implemented 
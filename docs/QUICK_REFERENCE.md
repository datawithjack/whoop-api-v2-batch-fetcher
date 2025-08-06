# WHOOP API V2 - Quick Reference

## 🚀 Quick Commands

### Authentication
```bash
# Single user auth
python src/whoop_authenication_simple.py

# Batch user auth
python src/whoop_authenication_batch.py

# Check tokens
python -c "import pickle; print(len(pickle.load(open('whoop_user_tokens.pkl','rb'))))"
```

### Data Fetching
```bash
# Fetch sleep data
python Scripts/fetch_sleep_data_v2.py

# Test endpoints
python src/whoop_sleep_end_point_tester.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "WHOOP_CLIENT_ID=your_id" > .env
echo "WHOOP_CLIENT_SECRET=your_secret" >> .env
echo "WHOOP_REDIRECT_URI=your_uri" >> .env
```

## 📋 Common Code Snippets

### Load Tokens
```python
import pickle
with open("whoop_user_tokens.pkl", 'rb') as f:
    tokens = pickle.load(f)
```

### Make API Request
```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.get(endpoint, headers=headers, params=params)
```

### Format Date for API
```python
from datetime import datetime
date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
```

### Handle Pagination
```python
next_token = None
while True:
    params = {'limit': 25}
    if next_token:
        params['nextToken'] = next_token
    
    response = requests.get(endpoint, headers=headers, params=params)
    data = response.json()
    
    records = data.get('records', [])
    # Process records...
    
    next_token = data.get('next_token')
    if not next_token:
        break
```

## 🔧 Error Codes & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `400 Bad Request` | Invalid parameters | Check limit ≤ 25, date format |
| `401 Unauthorized` | Expired token | Re-authenticate user |
| `403 Forbidden` | Missing scope | Check app permissions |
| `429 Rate Limited` | Too many requests | Wait 60 seconds, retry |

## 📊 Data Structures

### Token Format
```python
{
    "user@email.com": {
        "access_token": "string",
        "refresh_token": "string",
        "whoop_user_id": "string",
        "expires_at": "timestamp"
    }
}
```

### Sleep Record Format
```python
{
    "id": "string",
    "start": "2024-08-01T22:00:00.000Z",
    "end": "2024-08-02T06:30:00.000Z",
    "score": {"sleep_performance_percentage": 85.5},
    "sleep_need": {...},
    "sleep_consistency": {...}
}
```

## 🛠️ Debug Commands

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Token Validity
```python
def is_token_valid(token_info):
    return 'access_token' in token_info and 'whoop_user_id' in token_info
```

### Validate Response
```python
def is_valid_response(response):
    return response.status_code == 200 and 'records' in response.json()
```

## 📈 Analysis Functions

### Calculate Sleep Duration
```python
def get_sleep_duration(record):
    start = datetime.fromisoformat(record['start'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(record['end'].replace('Z', '+00:00'))
    return (end - start).total_seconds() / 3600  # hours
```

### Get Sleep Score
```python
def get_sleep_score(record):
    return record.get('score', {}).get('sleep_performance_percentage')
```

### Calculate Averages
```python
def calculate_averages(records):
    durations = [get_sleep_duration(r) for r in records if 'start' in r and 'end' in r]
    scores = [get_sleep_score(r) for r in records if get_sleep_score(r) is not None]
    
    return {
        'avg_duration': sum(durations) / len(durations) if durations else 0,
        'avg_score': sum(scores) / len(scores) if scores else 0
    }
```

## 🔍 Troubleshooting

### Common Issues

1. **"No token file found"**
   ```bash
   # Run authentication first
   python src/whoop_authenication_simple.py
   ```

2. **"401 Unauthorized"**
   ```python
   # Re-authenticate user
   # Delete whoop_user_tokens.pkl and re-run auth
   ```

3. **"400 Bad Request"**
   ```python
   # Check limit parameter (must be ≤ 25)
   params = {'limit': 25}  # Not 100
   ```

4. **"429 Rate Limited"**
   ```python
   # Add delay between requests
   import time
   time.sleep(60)  # Wait 60 seconds
   ```

### Quick Fixes

```python
# Fix date format
from datetime import datetime
date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# Fix limit parameter
params = {'limit': 25}  # Maximum allowed

# Add error handling
try:
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Request failed: {e}")
```

## 📝 File Naming Conventions

### Generated Files
- `sleep_data_v2_YYYYMMDD_HHMMSS.json` - Sleep data
- `sleep_data_summary_YYYYMMDD_HHMMSS.txt` - Summary report
- `whoop_user_tokens.pkl` - Authentication tokens
- `users.csv` - User configuration

### Cache Files
- `cache_*.json` - Cached API responses
- `api_usage.log` - API usage logs

## 🚀 Performance Tips

### Rate Limiting
```python
# Add delays
import time
time.sleep(1)  # 1 second between requests
time.sleep(2)  # 2 seconds between users
```

### Batch Processing
```python
# Process in smaller batches
batch_size = 5
for i in range(0, len(users), batch_size):
    batch = users[i:i + batch_size]
    # Process batch
    time.sleep(5)  # Delay between batches
```

### Memory Management
```python
# Process records one at a time
for record in records:
    process_record(record)
    # Don't keep all records in memory
```

## 📚 API Limits

### Rate Limits
- **Requests per minute**: Varies by endpoint
- **Records per request**: Maximum 25
- **Concurrent requests**: Limited per user

### Data Limits
- **Date range**: Up to 1 year
- **Pagination**: Automatic with nextToken
- **File size**: No specific limit

## 🔐 Security Notes

### Token Storage
- Tokens stored in `whoop_user_tokens.pkl`
- Keep this file secure
- Don't commit to version control

### Environment Variables
```bash
# Use .env file for secrets
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_client_secret
WHOOP_REDIRECT_URI=your_redirect_uri
```

---

**Quick Reference Version**: 1.0  
**Last Updated**: August 2024  
**Coverage**: Essential commands and patterns 
# WHOOP API V2 - Endpoint Index

## 🔗 Base URL
```
https://api.prod.whoop.com/developer/v2/
```

## 📋 Authentication Endpoints

### OAuth Token Exchange
```
POST https://api.prod.whoop.com/oauth/token
```

**Purpose**: Exchange authorization code for access token  
**Status**: ✅ Working  
**Used in**: `whoop_authenication_simple.py`, `whoop_authenication_batch.py`

**Request Body**:
```json
{
  "grant_type": "authorization_code",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "code": "authorization_code",
  "redirect_uri": "your_redirect_uri"
}
```

**Response**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 📊 Data Endpoints

### Sleep Data (v2)
```
GET https://api.prod.whoop.com/developer/v2/activity/sleep
```

**Purpose**: Fetch sleep data for authenticated user  
**Status**: ✅ Working  
**Used in**: `fetch_sleep_data_v2.py`, `whoop_sleep_end_point_tester.py`

**Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `start` | string | Yes | ISO 8601 start date | `2024-08-01T00:00:00.000Z` |
| `end` | string | Yes | ISO 8601 end date | `2024-08-31T23:59:59.999Z` |
| `limit` | integer | No | Records per request (max 25) | `25` |
| `nextToken` | string | No | Pagination token | `abc123...` |

**Response Structure**:
```json
{
  "records": [
    {
      "id": "string",
      "start": "2024-08-01T22:00:00.000Z",
      "end": "2024-08-02T06:30:00.000Z",
      "score": {
        "sleep_performance_percentage": 85.5
      },
      "sleep_need": {
        "baseline_milliseconds": 28800000,
        "need_from_sleep_debt_milliseconds": 0,
        "need_from_recent_strain_milliseconds": 0,
        "need_from_recent_naps_milliseconds": 0
      },
      "sleep_consistency": {
        "sleep_consistency_percentage": 92.3
      }
    }
  ],
  "next_token": "string"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters (e.g., limit > 25)
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Missing required scope
- `429 Too Many Requests`: Rate limit exceeded

## 🔍 Endpoint Testing

### Test Scripts
1. **`whoop_sleep_end_point_tester.py`**: Tests sleep endpoint functionality
2. **`fetch_sleep_data_v2.py`**: Production sleep data fetcher

### Test Coverage
- ✅ Parameter validation
- ✅ Error handling
- ✅ Pagination
- ✅ Rate limiting
- ✅ Token expiration
- ✅ Data parsing

## 📈 Data Analysis

### Sleep Metrics Available
- **Sleep Duration**: Calculated from start/end times
- **Sleep Score**: Performance percentage
- **Sleep Need**: Baseline and additional needs
- **Sleep Consistency**: Consistency percentage
- **Sleep Debt**: Accumulated sleep debt

### Analysis Functions
```python
def analyze_sleep_data(sleep_data):
    """Analyze sleep patterns and provide insights"""
    # Average sleep duration
    # Average sleep score
    # Sleep consistency trends
    # Sleep debt analysis
```

## 🛠️ Development Utilities

### Common Headers
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

### Date Formatting
```python
from datetime import datetime, timedelta

# ISO 8601 format required by API
start_date = datetime.now() - timedelta(days=30)
formatted_date = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
```

### Pagination Handling
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

## 🔐 Authentication Flow

### OAuth 2.0 Authorization Code Flow
1. **Authorization Request**: User authorizes app
2. **Code Exchange**: Exchange code for tokens
3. **Token Storage**: Store tokens securely
4. **Token Refresh**: Handle token expiration

### Token Management
```python
# Load stored tokens
with open("whoop_user_tokens.pkl", 'rb') as f:
    user_tokens = pickle.load(f)

# Access token for API calls
access_token = user_tokens[user_id]['access_token']
```

## 📊 Rate Limiting

### Limits
- **Requests per minute**: Varies by endpoint
- **Records per request**: Maximum 25 for sleep endpoint
- **Concurrent requests**: Limited per user

### Handling Rate Limits
```python
if response.status_code == 429:
    print("Rate limited - waiting 60 seconds...")
    time.sleep(60)
    continue
```

## 🔍 Error Handling

### Common Error Codes
| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check parameter format |
| 401 | Unauthorized | Re-authenticate user |
| 403 | Forbidden | Check app permissions |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry later |

### Error Response Format
```json
{
  "errors": ["Error message description"]
}
```

## 📝 Development Notes

### Best Practices
1. **Always handle pagination**: Use nextToken for large datasets
2. **Implement rate limiting**: Add delays between requests
3. **Validate responses**: Check for expected data structure
4. **Log errors**: Include detailed error information
5. **Test thoroughly**: Test with multiple users and scenarios

### Debugging Tips
1. **Enable debug logging**: `logging.basicConfig(level=logging.DEBUG)`
2. **Check token expiration**: Verify token validity before requests
3. **Validate parameters**: Ensure date formats and limits are correct
4. **Monitor rate limits**: Track request frequency

---

**Last Updated**: August 2024  
**API Version**: v2  
**Documentation Status**: Complete 
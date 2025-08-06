# WHOOP API V2 - Code Index

## 📁 File Structure Overview

### Core Authentication Files
| File | Purpose | Key Functions | Dependencies |
|------|---------|---------------|--------------|
| `src/whoopy_auth_batch.py` | Batch user authentication | `batch_authentication()`, `authenticate_single_user()` | asyncio, requests, pandas |
| `src/whoopy_auth_custom.py` | Single user authentication | `custom_whoop_auth()`, `test_credentials()` | asyncio, requests |
| `src/token_refresh_handler.py` | Token management utilities | `refresh_access_token()`, `handle_token_refresh()` | requests, datetime |

### Data Fetching Files
| File | Purpose | Key Functions | Dependencies |
|------|---------|---------------|--------------|
| `src/batch_sleep_fetcher.py` | Batch sleep data collection | `process_user()`, `fetch_user_sleep_data()` | requests, csv, json |
| `src/custom_sleep_fetcher.py` | Single user sleep data | `fetch_sleep_data()`, `export_sleep_data_to_csv()` | requests, csv, json |
| `src/expand_and_combine_sleep_data.py` | Data processing & combination | `process_sleep_json_file()`, `expand_nested_fields()` | json, csv, glob |

## 🔧 Function Index by Category

### 🔐 Authentication Functions

#### Batch Authentication (`whoopy_auth_batch.py`)
```python
# Configuration & Setup
def create_whoop_config() -> dict
    """Create WHOOP configuration from environment variables"""
    # Returns: {"client_id": str, "client_secret": str, "redirect_uri": str}

def load_users_from_csv(csv_file="users.csv") -> list
    """Load users from CSV file with validation"""
    # Returns: List of user dictionaries with email, first_name, last_name

# Credential Management
def save_batch_credentials(all_credentials: dict) -> None
    """Save batch credentials to .whoop_credentials_batch.json"""

def load_batch_credentials() -> dict
    """Load existing batch credentials from file"""

# Core Authentication
async def authenticate_single_user(user: dict, config: dict, scopes: str) -> dict
    """Authenticate a single user following OAuth 2.0 flow"""
    # Returns: User credentials dictionary or None

async def get_user_profile(access_token: str) -> dict
    """Get user profile information from WHOOP API"""

async def refresh_user_token(user_email: str, refresh_token: str, config: dict) -> bool
    """Refresh access token for a specific user"""

# Testing & Validation
async def test_batch_credentials(all_credentials: dict) -> bool
    """Test all batch credentials against WHOOP API"""

async def batch_authentication() -> bool
    """Main batch authentication orchestrator"""

# Utility Functions
def list_batch_users() -> None
    """List all batch authenticated users with status"""

def main() -> None
    """Main function with interactive menu"""
```

#### Custom Authentication (`whoopy_auth_custom.py`)
```python
# Configuration
def create_whoop_config() -> dict
    """Create WHOOP configuration from environment variables"""

def save_config_to_file(config: dict) -> None
    """Save configuration to config.json for whoopy"""

def save_credentials(credentials: dict) -> None
    """Save credentials to .whoop_credentials.json"""

# Core Authentication
async def custom_whoop_auth() -> bool
    """Custom WHOOP authentication following OAuth 2.0 flow"""

async def refresh_access_token(refresh_token: str, config: dict) -> bool
    """Refresh access token using refresh token"""

async def test_credentials() -> bool
    """Test the saved credentials against WHOOP API"""

def main() -> None
    """Main function with credential checking"""
```

### 🔄 Token Management (`token_refresh_handler.py`)
```python
# Credential I/O
def load_credentials() -> dict
    """Load saved credentials from .whoop_credentials.json"""

def save_credentials(credentials: dict) -> None
    """Save credentials to .whoop_credentials.json"""

# Token Validation
def is_token_expired(credentials: dict) -> bool
    """Check if token is expired or will expire soon (within 5 minutes)"""

def refresh_access_token(credentials: dict) -> bool
    """Refresh access token using refresh token"""

def test_token(credentials: dict) -> bool
    """Test if the token is working against WHOOP API"""

# Main Handlers
def handle_token_refresh() -> bool
    """Main function to handle token refresh"""

def get_token_status() -> None
    """Get detailed token status information"""

def main() -> None
    """Main function with command-line options"""
```

### 😴 Sleep Data Fetching

#### Batch Sleep Fetcher (`batch_sleep_fetcher.py`)
```python
# Directory Management
def ensure_exports_directory() -> str
    """Ensure exports directory and subdirectories exist"""
    # Creates: exports/, exports/json/, exports/combined_csv/

# Credential Management
def load_batch_credentials() -> dict
    """Load saved batch credentials"""

def save_batch_credentials(credentials_dict: dict) -> None
    """Save updated batch credentials"""

# Token Management
def is_token_expired(credentials: dict) -> bool
    """Check if token is expired or will expire soon"""

def refresh_user_token_batch(credentials: dict) -> bool
    """Refresh access token for batch users"""

def test_user_token(credentials: dict) -> bool
    """Test if user token is valid"""

def check_token_validity(credentials: dict) -> bool
    """Check if token is still valid without refreshing"""

# Data Processing
def flatten_sleep_record(record: dict) -> dict
    """Flatten a sleep record for CSV export with expanded nested fields"""

def export_sleep_data_to_csv(sleep_records: list, exports_dir: str, user_email: str, start_date: datetime = None, end_date: datetime = None) -> str
    """Export sleep data to CSV files with date range in filename"""

# Date Range Functions
def get_date_range_from_user() -> tuple
    """Get start and end dates from user input with validation"""
    # Returns: (start_date: datetime, end_date: datetime)

# API Functions
def fetch_user_sleep_data(credentials: dict, start_date: datetime = None, end_date: datetime = None, days_back: int = 30) -> list
    """Fetch sleep data for a specific user with pagination and custom date range"""

def get_user_profile(credentials: dict) -> dict
    """Get user profile information"""

# Main Processing
def process_user(user_email: str, user_credentials: dict, exports_dir: str, start_date: datetime = None, end_date: datetime = None, days_back: int = 30) -> bool
    """Process a single user's sleep data with custom date range"""

def main() -> None
    """Main function to fetch sleep data for all users in batch with custom date range"""
```

#### Custom Sleep Fetcher (`custom_sleep_fetcher.py`)
```python
# Directory Management
def ensure_exports_directory() -> str
    """Ensure the exports directory exists"""

def load_credentials() -> dict
    """Load saved credentials"""

# Data Processing
def flatten_sleep_record(record: dict) -> dict
    """Flatten a sleep record for CSV export"""

def export_sleep_data_to_csv(sleep_records: list, exports_dir: str, user_email: str) -> str
    """Export sleep data to CSV files"""

# API Functions
def fetch_sleep_data(credentials: dict, days_back: int = 30) -> list
    """Fetch sleep data using custom authentication with pagination"""

def get_user_profile(credentials: dict) -> dict
    """Get user profile information"""

def main() -> None
    """Main function to fetch sleep data using custom authentication"""
```

### 📊 Data Processing (`expand_and_combine_sleep_data.py`)
```python
# File I/O
def load_json_file(filepath: str) -> dict
    """Load a JSON file and return the data"""

def find_sleep_json_files() -> list
    """Find all sleep data JSON files in various locations"""

def ensure_output_directory() -> str
    """Ensure the combined_csv output directory exists"""

# Data Processing
def expand_nested_fields(record: dict) -> dict
    """Expand nested fields in a sleep record with special score handling"""

def debug_score_fields(records: list) -> None
    """Debug function to examine score fields"""

def process_sleep_json_file(filepath: str) -> list
    """Process a single sleep JSON file and return expanded records"""

def get_all_fieldnames(records: list) -> list
    """Get all unique field names from all records"""

def main() -> None
    """Main function to expand and combine sleep data"""
```

## 📊 Data Structures

### Batch Credentials Format
```python
batch_credentials = {
    "user@example.com": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "access_token": "string",
        "refresh_token": "string",
        "expires_in": 3600,
        "expires_at": "2024-01-01T12:00:00",
        "token_type": "bearer",
        "scope": "read:recovery read:sleep read:workout read:profile offline",
        "auth_timestamp": "2024-01-01T11:00:00",
        "whoop_user_id": "string",
        "whoop_first_name": "John",
        "whoop_last_name": "Doe"
    }
}
```

### Custom Credentials Format
```python
custom_credentials = {
    "access_token": "string",
    "refresh_token": "string",
    "expires_in": 3600,
    "expires_at": "2024-01-01T12:00:00",
    "token_type": "bearer",
    "scope": "read:recovery read:sleep read:workout read:profile offline",
    "auth_timestamp": "2024-01-01T11:00:00"
}
```

### Sleep Data Format
```python
sleep_data = {
    "user_info": {
        "email": "user@example.com",
        "whoop_user_id": "string",
        "name": "John Doe"
    },
    "fetch_info": {
        "timestamp": "2024-01-01T12:00:00",
        "start_date": "2024-01-01",
        "end_date": "2024-01-30",
        "total_records": 30
    },
    "sleep_records": [
        {
            "id": "string",
            "start": "2024-01-01T22:00:00Z",
            "end": "2024-01-02T06:00:00Z",
            "score": {
                "sleep_performance_percentage": 85.5,
                "respiratory_rate": 14.2,
                "sleep_needed": {...},
                "stage_summary": {...}
            }
        }
    ]
}
```

## 🔍 Code Patterns

### API Request Pattern
```python
def make_api_request(endpoint: str, access_token: str, params: dict = None) -> dict:
    """Standard API request pattern with error handling"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("❌ 401: Unauthorized - Token may be expired")
            return None
        elif response.status_code == 403:
            print("❌ 403: Forbidden - Check app permissions")
            return None
        elif response.status_code == 429:
            print("❌ 429: Rate Limited - Waiting 60 seconds...")
            time.sleep(60)
            return make_api_request(endpoint, access_token, params)
        else:
            print(f"❌ {response.status_code}: Unexpected status")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None
```

### Pagination Pattern
```python
def fetch_all_pages(endpoint: str, access_token: str, params: dict) -> list:
    """Fetch all pages of data using pagination"""
    all_records = []
    next_token = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"  📄 Fetching page {page_count}...")
        
        current_params = params.copy()
        if next_token:
            current_params['nextToken'] = next_token
            
        response = make_api_request(endpoint, access_token, current_params)
        if not response:
            break
            
        records = response.get('records', [])
        if records:
            all_records.extend(records)
            print(f"    ✅ Retrieved {len(records)} records")
            
            next_token = response.get('next_token')
            if not next_token:
                print(f"    📄 No more pages available")
                break
        else:
            print(f"    📄 No records found in response")
            break
            
    return all_records
```

### Token Refresh Pattern
```python
def handle_token_refresh(credentials: dict) -> bool:
    """Standard token refresh pattern"""
    if is_token_expired(credentials):
        print("🔄 Token expired. Attempting refresh...")
        
        if refresh_access_token(credentials):
            if test_token(credentials):
                print("✅ Token refreshed successfully!")
                return True
            else:
                print("❌ Refreshed token failed test")
                return False
        else:
            print("❌ Token refresh failed")
            return False
    else:
        print("✅ Token is still valid")
        return True
```

### CSV Export Pattern
```python
def export_to_csv(records: list, filename: str, user_email: str = "user") -> str:
    """Standard CSV export pattern with field detection"""
    if not records:
        print("⚠️  No records to export")
        return None
    
    # Flatten records
    flattened_records = []
    for record in records:
        flat_record = flatten_record(record)
        flat_record['user_email'] = user_email
        flattened_records.append(flat_record)
    
    # Get all field names
    fieldnames = set()
    for record in flattened_records:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))
    
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_records)
    
    print(f"✅ CSV exported: {filename} ({len(flattened_records)} records)")
    return filename
```

## 🛠️ Utility Functions

### Date/Time Utilities
```python
def format_date_for_api(date: datetime) -> str:
    """Format date for WHOOP API (ISO 8601)"""
    return date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def calculate_date_range(days_back: int = 30) -> tuple:
    """Calculate date range for API requests"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date

def is_token_expired(credentials: dict) -> bool:
    """Check if token is expired or will expire soon (within 5 minutes)"""
    if 'expires_at' not in credentials:
        return True
    
    try:
        expires_at = datetime.fromisoformat(credentials['expires_at'])
        buffer_time = timedelta(minutes=5)
        return datetime.now() + buffer_time >= expires_at
    except:
        return True
```

### File I/O Utilities
```python
def ensure_directory_structure() -> str:
    """Ensure all required directories exist"""
    exports_dir = "exports"
    json_dir = os.path.join(exports_dir, "json")
    csv_dir = os.path.join(exports_dir, "combined_csv")
    
    for directory in [exports_dir, json_dir, csv_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    return exports_dir

def save_data_with_timestamp(data: dict, prefix: str, directory: str = ".") -> str:
    """Save data with timestamped filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(directory, f"{prefix}_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename
```

### Validation Utilities
```python
def validate_credentials(credentials: dict) -> bool:
    """Validate credential structure and required fields"""
    required_fields = ['access_token', 'expires_at']
    for field in required_fields:
        if field not in credentials:
            return False
    
    if is_token_expired(credentials):
        return False
    
    return True

def validate_sleep_record(record: dict) -> bool:
    """Validate sleep record structure"""
    required_fields = ['id', 'start', 'end']
    for field in required_fields:
        if field not in record:
            return False
    return True
```

## 📈 Analysis Functions

### Sleep Analysis
```python
def calculate_sleep_metrics(records: list) -> dict:
    """Calculate comprehensive sleep metrics"""
    total_duration = 0
    total_score = 0
    valid_scores = 0
    
    for record in records:
        # Calculate duration
        if 'start' in record and 'end' in record:
            try:
                start_time = datetime.fromisoformat(record['start'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(record['end'].replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds() / 3600
                total_duration += duration
            except:
                pass
        
        # Calculate score
        if 'score' in record and record['score']:
            score = record['score'].get('sleep_performance_percentage')
            if score is not None:
                total_score += score
                valid_scores += 1
    
    return {
        'avg_duration': total_duration / len(records) if records else 0,
        'avg_score': total_score / valid_scores if valid_scores > 0 else 0,
        'total_records': len(records)
    }
```

---

## 🔧 Configuration Patterns

### Environment Configuration
```python
def load_config() -> dict:
    """Load configuration from environment variables"""
    load_dotenv()
    
    return {
        'client_id': os.getenv('WHOOP_CLIENT_ID'),
        'client_secret': os.getenv('WHOOP_CLIENT_SECRET'),
        'redirect_uri': os.getenv('WHOOP_REDIRECT_URI')
    }
```

### User Configuration
```python
def load_users_from_csv(csv_file: str) -> list:
    """Load user configuration from CSV"""
    df = pd.read_csv(csv_file)
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
```

---

## 🚀 Development Workflows

### 1. Batch Authentication Flow
```python
# 1. Setup environment variables
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_client_secret
WHOOP_REDIRECT_URI=your_redirect_uri

# 2. Create users.csv with columns: email, first_name, last_name, password

# 3. Run batch authentication
python src/whoopy_auth_batch.py

# 4. Verify authentication
python src/whoopy_auth_batch.py  # Option 2: List users
python src/whoopy_auth_batch.py  # Option 3: Test credentials
```

### 2. Custom Authentication Flow
```python
# 1. Setup environment variables (same as batch)

# 2. Run custom authentication
python src/whoopy_auth_custom.py

# 3. Test credentials
python src/token_refresh_handler.py status
```

### 3. Data Fetching Flow
```python
# Batch fetching (multiple users) - now with custom date range
python src/batch_sleep_fetcher.py
# Prompts for start and end dates (YYYY-MM-DD format)

# Custom fetching (single user) - last 30 days
python src/custom_sleep_fetcher.py

# Token refresh if needed
python src/token_refresh_handler.py refresh
```

### 4. Data Processing Flow
```python
# 1. Fetch data first (see above)

# 2. Expand and combine data
python src/expand_and_combine_sleep_data.py

# 3. Check outputs in exports/combined_csv/
```

---

## 📁 File Organization

### Input Files
- `users.csv` - User list for batch authentication
- `.env` - Environment variables for API credentials
- `.whoop_credentials.json` - Single user credentials
- `.whoop_credentials_batch.json` - Batch user credentials

### Output Files
- `exports/json/` - Individual user JSON data files
- `exports/combined_csv/` - Combined and expanded CSV files
- `exports/` - Individual user CSV files
- `*.json` - Root directory JSON files (custom fetcher)

### Configuration Files
- `config.json` - WHOOP API configuration for whoopy
- `requirements.txt` - Python dependencies

---

## 🔧 Common Commands

### Authentication
```bash
# Batch authentication
python src/whoopy_auth_batch.py

# Custom authentication
python src/whoopy_auth_custom.py

# Token management
python src/token_refresh_handler.py status
python src/token_refresh_handler.py refresh
python src/token_refresh_handler.py test
```

### Data Fetching
```bash
# Batch fetching
python src/batch_sleep_fetcher.py

# Custom fetching
python src/custom_sleep_fetcher.py
```

### Data Processing
```bash
# Expand and combine data
python src/expand_and_combine_sleep_data.py
```

---

**Last Updated**: December 2024  
**Code Coverage**: Complete - All 7 source files documented  
**Patterns**: Standardized with comprehensive error handling  
**Efficiency**: Organized by function category for easy updates 
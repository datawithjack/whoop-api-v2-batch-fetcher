# WHOOP API V2 - Clean Project Structure

## 📁 **Essential Files**

### **Core Scripts (`src/`)**
```
src/
├── whoopy_auth_custom.py      # Custom OAuth authentication
├── custom_sleep_fetcher.py    # Main sleep data fetcher
├── token_refresh_handler.py   # Token refresh utility
└── test_credentials.py        # Credential testing
```

### **Configuration Files**
```
├── requirements.txt           # Python dependencies
├── .whoop_credentials.json   # Current authentication tokens
├── config.json               # App configuration
└── .env                      # Environment variables (not tracked)
```

### **Documentation**
```
├── README.md                 # Project overview
├── PROJECT_STRUCTURE.md      # This file
└── docs/                     # Detailed documentation
    ├── API_INDEX.md
    ├── CODE_INDEX.md
    ├── DEVELOPMENT_GUIDE.md
    └── QUICK_REFERENCE.md
```

### **Data Output**
```
├── exports/                  # CSV export folder
└── sleep_data_custom_*.json  # Recent sleep data exports
```

## 🚀 **Quick Start Commands**

### **1. Authentication**
```bash
python src/whoopy_auth_custom.py
```

### **2. Test Credentials**
```bash
python src/test_credentials.py
```

### **3. Fetch Sleep Data**
```bash
python src/custom_sleep_fetcher.py
```

### **4. Token Management**
```bash
# Check token status
python src/token_refresh_handler.py status

# Refresh expired tokens
python src/token_refresh_handler.py refresh

# Test token
python src/token_refresh_handler.py test
```

## 🧹 **Cleaned Up Files**

### **Removed (Unused/Old)**
- ❌ `src/whoopy_auth.py` - Old whoopy authentication
- ❌ `src/whoopy_sleep_fetcher.py` - Old whoopy sleep fetcher
- ❌ `src/fetch_sleep_data_v2.py` - Old custom sleep fetcher
- ❌ `src/whoop_sleep_end_point_tester.py` - Testing script
- ❌ `src/whoop_authenication_simple.py` - Old authentication
- ❌ `basic_script_v1.py` - Basic test script
- ❌ `check_whoopy_tokens.py` - Old token checker
- ❌ `refresh_tokens.py` - Old refresh script
- ❌ `check_token_status.py` - Old status checker
- ❌ `whoop_user_tokens.pkl` - Old token format
- ❌ `working_sleep_endpoints.txt` - Old endpoint list
- ❌ `working_whoop_endpoints.txt` - Old endpoint list
- ❌ `batch_auth_urls.json` - Old batch auth
- ❌ `batch_auth_urls.txt` - Old batch auth

## 📊 **Current Status**

### **✅ Working Solution**
- **Authentication**: Custom OAuth flow with proper scopes
- **Data Fetching**: Complete sleep data with pagination
- **Token Management**: Automatic refresh with fallback
- **Data Export**: CSV and JSON formats
- **Error Handling**: Comprehensive error management

### **🎯 Key Features**
- ✅ **Scope-compatible**: Only requests available scopes
- ✅ **Auto-refresh**: Handles token expiration automatically
- ✅ **Complete data**: All sleep record fields included
- ✅ **Multiple formats**: CSV and JSON exports
- ✅ **Error recovery**: Clear guidance for issues

## 🔄 **Token Expiration Handling**

### **Automatic (Primary)**
```bash
python src/custom_sleep_fetcher.py
# Automatically detects and refreshes expired tokens
```

### **Manual (Secondary)**
```bash
python src/token_refresh_handler.py refresh
# Manually refresh tokens
```

### **Full Re-auth (Fallback)**
```bash
python src/whoopy_auth_custom.py
# Complete re-authentication if refresh fails
```

## 📝 **Environment Variables Required**

Create a `.env` file with:
```
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_client_secret
WHOOP_REDIRECT_URI=http://localhost:8080
```

## 🎉 **Project is Now Clean and Ready!**

The project has been cleaned up to contain only the essential files needed for:
- ✅ WHOOP API authentication
- ✅ Sleep data fetching
- ✅ Token management
- ✅ Data export
- ✅ Error handling

All unused and outdated files have been removed for a cleaner, more maintainable codebase. 
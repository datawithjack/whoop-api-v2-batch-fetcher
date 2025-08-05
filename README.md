# WHOOP API v2 Batch Sleep Data Fetcher

A Python-based tool for fetching and processing sleep data from multiple WHOOP users using the WHOOP Developer API v2.

## 🚀 Features

- **Batch Processing**: Fetch sleep data for multiple authenticated users
- **Automatic Token Refresh**: Handles OAuth 2.0 token refresh automatically
- **Data Expansion**: Expands nested JSON fields into individual CSV columns
- **Organized Output**: Saves data in structured directories (JSON and CSV)
- **Error Handling**: Robust error handling with detailed logging
- **User Management**: Supports multiple user credentials with batch authentication

## 📋 Prerequisites

- Python 3.7+
- WHOOP Developer Account
- WHOOP API credentials (Client ID, Client Secret, Redirect URI)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd WHOOP_API_V2
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   WHOOP_CLIENT_ID=your_client_id
   WHOOP_CLIENT_SECRET=your_client_secret
   WHOOP_REDIRECT_URI=your_redirect_uri
   ```

## 📁 Project Structure

```
WHOOP_API_V2/
├── src/
│   ├── batch_sleep_fetcher.py          # Main batch processing script
│   ├── expand_and_combine_sleep_data.py # Data expansion and CSV creation
│   ├── token_refresh_handler.py        # Token refresh utilities
│   ├── custom_sleep_fetcher.py         # Single-user sleep fetcher
│   └── batch_whoopy_auth.py           # Batch authentication script
├── exports/
│   ├── json/                           # Individual JSON files per user
│   └── combined_csv/                   # Combined expanded CSV files
├── .env                                # Environment variables (not in repo)
├── .whoop_credentials_batch.json       # Batch user credentials (not in repo)
└── README.md
```

## 🔧 Usage

### 1. **Batch Authentication**
First, authenticate all users:
```bash
python src/batch_whoopy_auth.py
```

### 2. **Fetch Sleep Data**
Fetch sleep data for all authenticated users:
```bash
python src/batch_sleep_fetcher.py
```

### 3. **Expand and Combine Data**
Expand nested fields and create combined CSV:
```bash
python src/expand_and_combine_sleep_data.py
```

## 📊 Data Output

### **Individual JSON Files**
- Location: `exports/json/`
- Format: `sleep_data_batch_{user_email}_{timestamp}.json`
- Contains: Raw sleep data with user info and metadata

### **Combined CSV File**
- Location: `exports/combined_csv/`
- Format: `combined_sleep_data_expanded_{timestamp}.csv`
- Contains: All users' data with expanded nested fields

### **Expanded Fields**
The following nested fields are expanded into individual columns:

#### **Score Stage Summary:**
- `score.stage_summary.total_in_bed_time_milli`
- `score.stage_summary.total_awake_time_milli`
- `score.stage_summary.total_light_sleep_time_milli`
- `score.stage_summary.total_slow_wave_sleep_time_milli`
- `score.stage_summary.total_rem_sleep_time_milli`
- `score.stage_summary.sleep_cycle_count`
- `score.stage_summary.disturbance_count`

#### **Score Sleep Needed:**
- `score.sleep_needed.baseline_milli`
- `score.sleep_needed.need_from_sleep_debt_milli`
- `score.sleep_needed.need_from_recent_strain_milli`
- `score.sleep_needed.need_from_recent_nap_milli`

#### **Other Score Metrics:**
- `score.respiratory_rate`
- `score.sleep_performance_percentage`
- `score.sleep_consistency_percentage`
- `score.sleep_efficiency_percentage`

## 🔐 Security

- **Credentials**: Never commit `.env` or credential files to version control
- **Data Privacy**: Export files contain personal data and are excluded from git
- **Token Management**: Access tokens are automatically refreshed when needed

## 🐛 Troubleshooting

### **Token Refresh Issues**
If token refresh fails:
1. Check your `.env` file has correct credentials
2. Ensure redirect URI matches WHOOP app settings
3. Re-authenticate users if needed: `python src/batch_whoopy_auth.py`

### **No Data Retrieved**
- Verify users have sleep data for the specified date range
- Check API permissions in WHOOP Developer Console
- Ensure tokens are valid and not expired

### **Permission Errors**
- Verify WHOOP app has required scopes (sleep data access)
- Check user consent for data sharing

## 📝 API Reference

This project uses the [WHOOP Developer API v2](https://developer.whoop.com/docs/developing/api-reference/api-reference-v2).

### **Key Endpoints:**
- User Profile: `/developer/v2/user/profile/basic`
- Sleep Data: `/developer/v2/activity/sleep`
- Token Refresh: `/oauth/oauth2/token`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please respect WHOOP's terms of service and data privacy requirements.

## ⚠️ Disclaimer

This tool is not affiliated with WHOOP. Use responsibly and in accordance with WHOOP's developer terms and data privacy policies. 
# WHOOP Sleep Data Updater Guide

## Overview

The WHOOP Sleep Data Updater is designed to automatically fetch new sleep data and append it to existing CSV files. This system is perfect for maintaining up-to-date sleep data without having to re-fetch all historical data each time.

## Features

- **Incremental Updates**: Only fetches new data since the last update
- **Automatic Token Refresh**: Handles expired tokens automatically
- **Batch Processing**: Updates all users in batch credentials
- **CSV Append**: Safely appends new records to existing files
- **Scheduling**: Can run automatically at regular intervals
- **Error Handling**: Robust error handling and logging

## Prerequisites

1. **Existing Data**: You must have run `batch_sleep_fetcher.py` at least once to create initial CSV files
2. **Batch Credentials**: Valid `.whoop_credentials_batch.json` file
3. **Environment Variables**: WHOOP API credentials in `.env` file

## Quick Start

### 1. Manual Update (One-time)

```bash
# Run the updater once
python src/sleep_data_updater.py
```

### 2. Windows Batch File

```bash
# Double-click or run from command line
run_updater.bat
```

### 3. Automated Updates (Future)

The updater is designed to work well with:
- GitHub Actions
- Cron jobs
- Windows Task Scheduler
- Other CI/CD systems

## How It Works

### 1. User Discovery
- Loads all users from `.whoop_credentials_batch.json`
- Finds existing CSV files for each user

### 2. Date Detection
- Reads the existing CSV file to find the latest date
- Uses the `start` field to determine the most recent record

### 3. API Query
- Queries WHOOP API for data since the latest date + 1 day
- Handles pagination automatically
- Refreshes tokens if needed

### 4. Data Append
- Flattens new records using the same logic as the original fetcher
- Appends new records to the existing CSV file
- Maintains all existing columns and adds new ones if needed

## File Structure

```
exports/
├── sleep_data_batch_jackfrankandrew_at_gmail_com_20240101_20250806_20250806_103519.csv
├── sleep_data_batch_user2_at_gmail_com_*.csv
└── ...
```

## Scheduling Options

### 1. Every 6 Hours (Default)
```python
schedule.every(6).hours.do(run_updater)
```

### 2. Custom Schedule
Edit `src/schedule_updater.py` to change the schedule:

```python
# Every 4 hours
schedule.every(4).hours.do(run_updater)

# Twice daily at specific times
schedule.every().day.at("06:00").do(run_updater)
schedule.every().day.at("18:00").do(run_updater)

# Every 30 minutes
schedule.every(30).minutes.do(run_updater)
```

### 3. Windows Task Scheduler
Create a Windows Task to run `run_updater.bat` at regular intervals.

## Error Handling

The updater handles several types of errors:

- **Token Expiration**: Automatically refreshes expired tokens
- **API Rate Limits**: Waits 60 seconds and retries
- **Missing Files**: Skips users without existing CSV files
- **Network Issues**: Logs errors and continues with other users

## Logging

The updater provides detailed logging:

```
🔄 WHOOP Sleep Data Updater
==================================================
📋 Found 1 users in batch credentials

🔄 Processing user: jackfrankandrew@gmail.com
  📁 Found existing file: exports/sleep_data_batch_jackfrankandrew_at_gmail_com_20240101_20250806_20250806_103519.csv
  📅 Latest date in CSV: 2025-08-06 03:54:29
  📅 Fetching data from 2025-08-07 onwards...
    📄 Fetching page 1...
      ✅ Retrieved 0 records
    📄 No records found in response
  ✅ Total new records fetched: 0
  ⚠️  No new records to append

==================================================
✅ Update complete: 1/1 users processed successfully
```

## Troubleshooting

### No CSV Files Found
```
❌ No existing CSV file found for user@example.com
💡 Run batch_sleep_fetcher.py first to create initial data file
```

**Solution**: Run the initial batch fetcher first:
```bash
python src/batch_sleep_fetcher.py
```

### Token Refresh Failed
```
❌ Failed to refresh token
```

**Solution**: Check your `.env` file has correct WHOOP credentials:
```
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_client_secret
WHOOP_REDIRECT_URI=your_redirect_uri
```

### Permission Errors
```
❌ 403: Forbidden - Check app permissions
```

**Solution**: Verify your WHOOP app has the required scopes:
- `read:sleep`
- `read:profile`
- `offline`

## Performance Considerations

### API Rate Limits
- WHOOP API has rate limits
- The updater includes automatic retry logic
- Consider running updates during off-peak hours

### File Size
- CSV files grow over time
- Consider archiving old data periodically
- Monitor disk space usage

### Memory Usage
- The updater processes one user at a time
- Minimal memory footprint
- Suitable for long-running processes

## Database Integration

When you're ready to move to a database:

1. **Modify `append_to_csv()`**: Replace with database insert logic
2. **Update `get_latest_date_from_csv()`**: Query database for latest date
3. **Database Schema**: Use the same flattened structure as CSV

Example database integration:
```python
def append_to_database(db_connection, new_records, user_email):
    """Append new records to database instead of CSV"""
    cursor = db_connection.cursor()
    
    for record in new_records:
        # Insert into sleep_data table
        cursor.execute("""
            INSERT INTO sleep_data (
                user_email, start_time, end_time, sleep_score, ...
            ) VALUES (?, ?, ?, ?, ...)
        """, (user_email, record['start'], record['end'], record['score_sleep_performance_percentage'], ...))
    
    db_connection.commit()
```

## Best Practices

1. **Regular Updates**: Run updates every 6-12 hours for fresh data
2. **Monitor Logs**: Check for errors and failed updates
3. **Backup Data**: Keep backups of CSV files before major updates
4. **Test First**: Test the updater on a small dataset first
5. **Environment**: Use virtual environments for dependency management

## Security Notes

- Never commit `.env` or credential files to version control
- Store credentials securely
- Use environment variables for sensitive data
- Consider using a secrets management system for production

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for specific error messages
3. Verify your WHOOP API credentials and permissions
4. Ensure you have the latest version of the code

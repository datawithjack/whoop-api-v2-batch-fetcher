# GitHub Actions Setup Guide

## 🚀 **Complete Setup for Automated WHOOP Sleep Data Updates**

This guide will help you set up automated daily sleep data updates using GitHub Actions.

## 📋 **Prerequisites**

- ✅ WHOOP API credentials (client_id, client_secret, redirect_uri)
- ✅ Batch user authentication completed
- ✅ GitHub repository created
- ✅ Local sleep data updater working

## 🔧 **Step 1: Prepare Your Repository**

### **Files Already Created:**
- ✅ `data/` directory with your CSV file
- ✅ `.github/workflows/update_sleep_data.yml` - GitHub Actions workflow
- ✅ `src/sleep_data_updater_github.py` - GitHub Actions version of updater
- ✅ Updated `.gitignore` to allow data directory
- ✅ `requirements.txt` with dependencies

### **Repository Structure:**
```
WHOOP_API_V2/
├── .github/
│   └── workflows/
│       └── update_sleep_data.yml
├── data/
│   └── sleep_data_batch_jackfrankandrew_at_gmail_com.csv
├── src/
│   ├── sleep_data_updater_github.py
│   └── prepare_github_secrets.py
├── requirements.txt
└── .gitignore
```

## 🔐 **Step 2: Set Up GitHub Secrets**

### **Run the Preparation Script:**
```bash
python src/prepare_github_secrets.py
```

### **Required GitHub Secrets:**

1. **WHOOP_CLIENT_ID**
   - Value: Your WHOOP API client ID
   - Source: Your `.env` file

2. **WHOOP_CLIENT_SECRET**
   - Value: Your WHOOP API client secret
   - Source: Your `.env` file

3. **WHOOP_REDIRECT_URI**
   - Value: Your WHOOP API redirect URI
   - Source: Your `.env` file

4. **WHOOP_BATCH_CREDENTIALS**
   - Value: JSON string from the preparation script
   - Source: `github_secrets_batch_credentials.json` file

### **How to Add Secrets:**
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add each secret with the exact name and value

## 🧪 **Step 3: Test Locally**

### **Test with Environment Variables:**
```bash
# Set environment variables (Windows PowerShell)
$env:WHOOP_CLIENT_ID="your_client_id"
$env:WHOOP_CLIENT_SECRET="your_client_secret"
$env:WHOOP_REDIRECT_URI="your_redirect_uri"
$env:WHOOP_BATCH_CREDENTIALS='{"jackfrankandrew@gmail.com": {...}}'

# Run the GitHub Actions version
python src/sleep_data_updater_github.py
```

### **Expected Output:**
```
🔄 WHOOP Sleep Data Updater (GitHub Actions)
==================================================
📋 Found 1 users in batch credentials

🔄 Processing user: jackfrankandrew@gmail.com
  ✅ Current token is still valid!
  📁 Using file: data/sleep_data_batch_jackfrankandrew_at_gmail_com.csv
  📅 Latest date in CSV: 2025-08-05 21:17:57
  📅 Fetching data from 2025-08-05 onwards...
    📄 Fetching page 1...
      ✅ Retrieved 1 records
      📄 No more pages available
  ✅ Total new records fetched: 1
  ✅ Appended 1 new records to data/sleep_data_batch_jackfrankandrew_at_gmail_com.csv

==================================================
✅ Update complete: 1/1 users processed successfully
```

## 🚀 **Step 4: Deploy to GitHub**

### **Commit and Push:**
```bash
git add .
git commit -m "Add GitHub Actions workflow for automated sleep data updates"
git push origin main
```

### **Verify Workflow:**
1. Go to your GitHub repository
2. Click on the **Actions** tab
3. You should see the "Update WHOOP Sleep Data" workflow
4. Click **"Run workflow"** to test manually

## ⏰ **Step 5: Schedule Configuration**

### **Current Schedule:**
- **Time**: Daily at 6:00 AM UTC
- **Cron**: `0 6 * * *`

### **To Change Schedule:**
Edit `.github/workflows/update_sleep_data.yml`:
```yaml
on:
  schedule:
    # Examples:
    - cron: '0 6 * * *'    # Daily at 6 AM UTC
    - cron: '0 12 * * *'   # Daily at 12 PM UTC
    - cron: '0 18 * * 1-5' # Weekdays at 6 PM UTC
```

### **Manual Trigger:**
- Go to Actions tab
- Click "Update WHOOP Sleep Data"
- Click "Run workflow"

## 🔄 **Step 6: Token Management**

### **When Tokens Expire:**
1. **Run locally**: `python src/sleep_data_updater.py`
2. **Check output**: Look for token refresh messages
3. **Update GitHub Secret**: 
   - Run `python src/prepare_github_secrets.py`
   - Copy new JSON to GitHub Secrets
   - Update `WHOOP_BATCH_CREDENTIALS` secret

### **Token Refresh Process:**
```bash
# 1. Run the updater (will refresh tokens)
python src/sleep_data_updater.py

# 2. Prepare new credentials for GitHub
python src/prepare_github_secrets.py

# 3. Update GitHub Secret with new JSON
```

## 📊 **Step 7: Monitor and Maintain**

### **Check Workflow Status:**
- **GitHub Actions tab**: View run history and logs
- **Email notifications**: Configure in repository settings
- **Data directory**: Check for updated CSV files

### **Troubleshooting:**
- **Workflow fails**: Check Actions tab for error logs
- **No new data**: Verify tokens are valid
- **Rate limiting**: WHOOP API has limits, workflow includes delays

### **Data Backup:**
- CSV files are versioned in Git
- Each run commits changes automatically
- Historical data is preserved

## 🎯 **Success Indicators**

✅ **Workflow runs successfully**  
✅ **New sleep data appears in CSV files**  
✅ **Git commits show daily updates**  
✅ **No authentication errors in logs**  

## 🔧 **Customization Options**

### **Add More Users:**
1. Run `python src/whoopy_auth_batch.py`
2. Add new users to batch authentication
3. Update GitHub Secrets with new credentials

### **Change Data Format:**
- Modify `flatten_sleep_record()` in the updater
- Add new fields as needed
- CSV structure will adapt automatically

### **Adjust Schedule:**
- Edit cron expression in workflow file
- Consider timezone differences
- WHOOP data availability (may have delays)

## 🆘 **Support**

### **Common Issues:**
- **401 Unauthorized**: Tokens expired, need refresh
- **400 Bad Request**: API parameter issues (rare)
- **429 Rate Limited**: Too many requests, wait and retry

### **Getting Help:**
- Check GitHub Actions logs for detailed error messages
- Verify all secrets are set correctly
- Test locally before deploying

---

**🎉 Congratulations!** Your automated WHOOP sleep data collection system is now ready to run daily on GitHub Actions.

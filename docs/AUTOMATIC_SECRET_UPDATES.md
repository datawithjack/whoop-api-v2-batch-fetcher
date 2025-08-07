# Automatic GitHub Secret Updates

## 🚀 **Overview**

The WHOOP API v2 project now includes **automatic GitHub Secret updates** when tokens are refreshed. This eliminates the need for manual intervention when WHOOP access tokens expire.

## 🔄 **How It Works**

### **1. Token Expiry Detection**
- Workflow checks if tokens are expired or will expire within 5 minutes
- Uses the `is_token_expired()` function to determine if refresh is needed

### **2. Automatic Token Refresh**
- Calls WHOOP API refresh endpoint with existing refresh token
- Updates access token, refresh token, and expiration time
- Tests the new token to ensure it's valid

### **3. Secret Update Process**
- Saves updated credentials to `updated_credentials.json`
- GitHub CLI updates the `WHOOP_BATCH_CREDENTIALS` secret
- Cleans up temporary files after successful update

### **4. Workflow Integration**
```yaml
- name: Update GitHub Secrets (if needed)
  if: always()
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    if [ -f "updated_credentials.json" ]; then
      echo "🔄 Updating WHOOP_BATCH_CREDENTIALS secret..."
      gh secret set WHOOP_BATCH_CREDENTIALS --body "$(cat updated_credentials.json)" --repo ${{ github.repository }}
      echo "✅ Secret updated successfully!"
      rm -f updated_credentials.json
    else
      echo "ℹ️  No credential updates needed"
    fi
```

## 🔧 **Requirements**

### **GitHub Actions Permissions**
```yaml
permissions:
  contents: write
  actions: write  # Required for updating secrets
```

### **GitHub CLI Installation**
The workflow automatically installs GitHub CLI:
```yaml
- name: Install GitHub CLI
  run: |
    type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt update \
    && sudo apt install gh -y
```

## 🧪 **Testing**

### **Test GitHub CLI Functionality**
```bash
python src/test_github_cli.py
```

### **Test Complete Workflow Locally**
```bash
# Set environment variables
export WHOOP_CLIENT_ID="your_client_id"
export WHOOP_CLIENT_SECRET="your_client_secret"
export WHOOP_REDIRECT_URI="your_redirect_uri"
export WHOOP_BATCH_CREDENTIALS='{"user@example.com": {...}}'

# Run the updater
python src/sleep_data_updater_github.py
```

### **Check for Updated Credentials**
```bash
# Look for the temporary file
ls -la updated_credentials.json

# If found, manually update the secret (for testing)
gh secret set WHOOP_BATCH_CREDENTIALS --body "$(cat updated_credentials.json)" --repo <your-repo>

# Clean up
rm -f updated_credentials.json
```

## 📊 **Monitoring**

### **Workflow Logs**
Look for these messages in GitHub Actions logs:
```
🔄 Token has expired. Attempting automatic refresh...
✅ Token refreshed successfully!
📅 New expiration: 2025-08-07 07:31:04.959978
🔄 Credentials will be automatically updated in GitHub Secrets
💾 Updated credentials saved for GitHub Secrets update
🔄 Updating WHOOP_BATCH_CREDENTIALS secret...
✅ Secret updated successfully!
```

### **Success Indicators**
- ✅ Token refresh messages in logs
- ✅ "Secret updated successfully!" message
- ✅ No manual intervention required
- ✅ Workflow continues to run daily

## 🆘 **Troubleshooting**

### **Common Issues**

#### **1. GitHub CLI Installation Fails**
```
❌ Error: Unable to install GitHub CLI
```
**Solution**: Check if the workflow has proper permissions and internet access.

#### **2. Secret Update Permission Denied**
```
❌ Error: Resource not accessible by integration
```
**Solution**: Ensure the workflow has `actions: write` permission.

#### **3. Token Refresh Fails**
```
❌ Token refresh failed: 400
```
**Solution**: The refresh token may be invalid. User needs manual re-authentication.

#### **4. GitHub CLI Not Authenticated**
```
❌ Error: not logged in to any hosts
```
**Solution**: This shouldn't happen in GitHub Actions as it uses `GITHUB_TOKEN`.

### **Manual Fallback**
If automatic updates fail:
1. Run `python src/sleep_data_updater_github.py` locally
2. Check for `updated_credentials.json` file
3. Manually update the GitHub secret:
   ```bash
   gh secret set WHOOP_BATCH_CREDENTIALS --body "$(cat updated_credentials.json)" --repo <your-repo>
   ```

## 🔒 **Security Considerations**

### **Token Security**
- Refresh tokens are stored securely in GitHub Secrets
- Access tokens are never logged or exposed
- Temporary files are cleaned up after use

### **Permission Scope**
- Workflow only updates the specific secret (`WHOOP_BATCH_CREDENTIALS`)
- Uses minimal required permissions (`actions: write`)
- No access to other repository secrets

### **Audit Trail**
- All secret updates are logged in GitHub Actions
- Token refresh events are tracked in WHOOP API logs
- Credential changes are versioned in the workflow

## 📈 **Benefits**

### **Automation**
- ✅ No manual intervention required
- ✅ Tokens refresh automatically before expiry
- ✅ Workflow continues uninterrupted

### **Reliability**
- ✅ Reduces human error in secret management
- ✅ Ensures tokens are always current
- ✅ Prevents workflow failures due to expired tokens

### **Maintenance**
- ✅ Eliminates manual secret update process
- ✅ Reduces administrative overhead
- ✅ Self-healing token management

## 🎯 **Best Practices**

1. **Monitor Workflow Logs**: Check for token refresh messages regularly
2. **Test Locally**: Use the test script to verify functionality
3. **Backup Credentials**: Keep a local copy of credentials for emergencies
4. **Review Permissions**: Ensure minimal required permissions are set
5. **Update Documentation**: Keep this guide current with any changes

---

**🎉 Congratulations!** Your WHOOP sleep data collection system now has fully automated token management with automatic GitHub Secret updates.

import json
import os
from datetime import datetime

def prepare_github_secrets():
    """Prepare batch credentials for GitHub Secrets"""
    print("🔧 GitHub Secrets Preparation Tool")
    print("=" * 50)
    
    # Load current batch credentials
    try:
        with open(".whoop_credentials_batch.json", "r") as f:
            batch_credentials = json.load(f)
    except FileNotFoundError:
        print("❌ No batch credentials file found. Please run batch authentication first:")
        print("   python src/whoopy_auth_batch.py")
        return
    except Exception as e:
        print(f"❌ Error loading batch credentials: {e}")
        return
    
    print(f"📋 Found {len(batch_credentials)} users in batch credentials")
    
    # Convert to JSON string for GitHub Secrets
    credentials_json = json.dumps(batch_credentials, indent=2)
    
    print("\n🔐 GitHub Secrets Setup Instructions")
    print("=" * 50)
    print("1. Go to your GitHub repository")
    print("2. Navigate to Settings → Secrets and variables → Actions")
    print("3. Click 'New repository secret' for each of the following:")
    print()
    
    # Get environment variables
    client_id = os.getenv('WHOOP_CLIENT_ID')
    client_secret = os.getenv('WHOOP_CLIENT_SECRET')
    redirect_uri = os.getenv('WHOOP_REDIRECT_URI')
    
    print("📝 Required GitHub Secrets:")
    print()
    
    if client_id:
        print("✅ WHOOP_CLIENT_ID")
        print(f"   Value: {client_id}")
    else:
        print("❌ WHOOP_CLIENT_ID (not found in .env)")
    
    print()
    
    if client_secret:
        print("✅ WHOOP_CLIENT_SECRET")
        print(f"   Value: {client_secret}")
    else:
        print("❌ WHOOP_CLIENT_SECRET (not found in .env)")
    
    print()
    
    if redirect_uri:
        print("✅ WHOOP_REDIRECT_URI")
        print(f"   Value: {redirect_uri}")
    else:
        print("❌ WHOOP_REDIRECT_URI (not found in .env)")
    
    print()
    print("✅ WHOOP_BATCH_CREDENTIALS")
    print("   Value: (JSON string below)")
    print()
    print("📋 Copy this entire JSON string:")
    print("-" * 50)
    print(credentials_json)
    print("-" * 50)
    
    # Save to file for easy copying
    output_file = "github_secrets_batch_credentials.json"
    with open(output_file, "w") as f:
        f.write(credentials_json)
    
    print(f"\n💾 Also saved to: {output_file}")
    print("\n⚠️  Important Notes:")
    print("• Keep these secrets secure - never commit them to the repository")
    print("• When tokens expire, you'll need to update WHOOP_BATCH_CREDENTIALS")
    print("• The workflow will run daily at 6:00 AM UTC")
    print("• You can manually trigger the workflow from the Actions tab")

if __name__ == "__main__":
    prepare_github_secrets()

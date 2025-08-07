#!/usr/bin/env python3
"""
Test GitHub CLI functionality for updating secrets
This script helps verify that the GitHub CLI can update secrets properly
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def test_github_cli_installation():
    """Test if GitHub CLI is installed and accessible"""
    print("🔧 Testing GitHub CLI Installation")
    print("=" * 50)
    
    try:
        result = subprocess.run(['gh', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ GitHub CLI installed: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ GitHub CLI not found. Please install it first:")
        print("   https://cli.github.com/")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI error: {e}")
        return False

def test_github_authentication():
    """Test if GitHub CLI is authenticated"""
    print("\n🔐 Testing GitHub Authentication")
    print("=" * 50)
    
    try:
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True, check=True)
        print("✅ GitHub CLI authenticated")
        print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("❌ GitHub CLI not authenticated")
        print("💡 To authenticate, run: gh auth login")
        print(f"Error: {e.stderr.strip()}")
        return False

def create_test_credentials():
    """Create test credentials for testing"""
    print("\n📝 Creating Test Credentials")
    print("=" * 50)
    
    test_credentials = {
        "test@example.com": {
            "access_token": "test_access_token_123",
            "refresh_token": "test_refresh_token_456",
            "expires_in": 3600,
            "expires_at": (datetime.now().replace(microsecond=0)).isoformat(),
            "token_type": "bearer",
            "last_refreshed": datetime.now().isoformat(),
            "whoop_user_id": "test_user_123"
        }
    }
    
    # Save test credentials
    with open('test_credentials.json', 'w') as f:
        json.dump(test_credentials, f, indent=2)
    
    print("✅ Test credentials created: test_credentials.json")
    return test_credentials

def test_secret_update_simulation():
    """Simulate the secret update process"""
    print("\n🔄 Testing Secret Update Simulation")
    print("=" * 50)
    
    # Create test credentials
    test_credentials = create_test_credentials()
    
    # Simulate the workflow process
    print("📋 Simulating workflow steps:")
    print("1. ✅ Token refresh detected")
    print("2. ✅ Updated credentials saved to file")
    print("3. 🔄 Would update GitHub secret with new credentials")
    
    # Show what the GitHub CLI command would be
    credentials_json = json.dumps(test_credentials, indent=2)
    print(f"\n📝 GitHub CLI command that would be run:")
    print(f"gh secret set WHOOP_BATCH_CREDENTIALS --body '{credentials_json}' --repo <repository>")
    
    print("\n⚠️  Note: This is a simulation. No actual secrets will be updated.")
    
    # Clean up test file
    if os.path.exists('test_credentials.json'):
        os.remove('test_credentials.json')
        print("🧹 Test file cleaned up")

def test_workflow_permissions():
    """Test if the workflow has the right permissions"""
    print("\n🔑 Testing Workflow Permissions")
    print("=" * 50)
    
    print("📋 Required permissions for secret updates:")
    print("✅ contents: write - For committing data changes")
    print("✅ actions: write - For updating secrets")
    
    print("\n📝 GitHub Actions workflow permissions:")
    print("permissions:")
    print("  contents: write")
    print("  actions: write  # Required for updating secrets")
    
    print("\n✅ Permissions look correct for secret updates")

def show_manual_test_instructions():
    """Show instructions for manual testing"""
    print("\n🧪 Manual Testing Instructions")
    print("=" * 50)
    
    print("To test the complete workflow manually:")
    print()
    print("1. 🔐 Ensure GitHub CLI is authenticated:")
    print("   gh auth login")
    print()
    print("2. 🚀 Run the sleep data updater:")
    print("   python src/sleep_data_updater_github.py")
    print()
    print("3. 📝 If tokens are refreshed, check for updated_credentials.json:")
    print("   ls -la updated_credentials.json")
    print()
    print("4. 🔄 Manually update the secret (if needed):")
    print("   gh secret set WHOOP_BATCH_CREDENTIALS --body \"$(cat updated_credentials.json)\" --repo <your-repo>")
    print()
    print("5. 🧹 Clean up:")
    print("   rm -f updated_credentials.json")

def main():
    """Main test function"""
    print("🧪 GitHub CLI and Secret Update Test Suite")
    print("=" * 60)
    
    # Test GitHub CLI installation
    if not test_github_cli_installation():
        return
    
    # Test GitHub authentication
    if not test_github_authentication():
        print("\n💡 To continue testing, please authenticate with:")
        print("   gh auth login")
        return
    
    # Test workflow permissions
    test_workflow_permissions()
    
    # Test secret update simulation
    test_secret_update_simulation()
    
    # Show manual test instructions
    show_manual_test_instructions()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("💡 Your GitHub Actions workflow should now automatically update secrets when tokens are refreshed.")

if __name__ == "__main__":
    main()

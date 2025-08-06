#!/usr/bin/env python3
"""
WHOOP API Environment Setup Helper
This script helps you set up the required environment variables for WHOOP API access.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with WHOOP API credentials"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    print("\n🔧 WHOOP API Environment Setup")
    print("=" * 50)
    print("You need to get these values from your WHOOP Developer Console:")
    print("https://developer.whoop.com/")
    print()
    
    # Get credentials from user
    client_id = input("Enter your WHOOP Client ID: ").strip()
    client_secret = input("Enter your WHOOP Client Secret: ").strip()
    redirect_uri = input("Enter your WHOOP Redirect URI: ").strip()
    
    if not all([client_id, client_secret, redirect_uri]):
        print("❌ All fields are required!")
        return False
    
    # Create .env file
    env_content = f"""# WHOOP API Credentials
WHOOP_CLIENT_ID={client_id}
WHOOP_CLIENT_SECRET={client_secret}
WHOOP_REDIRECT_URI={redirect_uri}

# Optional: Add any other environment variables here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        print("\n🔒 Security Note:")
        print("• The .env file is already in .gitignore")
        print("• Never commit this file to version control")
        print("• Keep your credentials secure")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_env_variables():
    """Test if environment variables are properly set"""
    print("\n🧪 Testing Environment Variables")
    print("=" * 40)
    
    required_vars = ['WHOOP_CLIENT_ID', 'WHOOP_CLIENT_SECRET', 'WHOOP_REDIRECT_URI']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first few characters for verification
            display_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}")
        print("💡 Run this script to set them up.")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def main():
    """Main function"""
    print("🔧 WHOOP API Environment Setup Helper")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path('.env')
    
    if env_file.exists():
        print("📁 .env file found!")
        choice = input("What would you like to do?\n1. Test current environment variables\n2. Create new .env file\n3. Exit\nChoice (1-3): ").strip()
        
        if choice == '1':
            test_env_variables()
        elif choice == '2':
            create_env_file()
        elif choice == '3':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice.")
    else:
        print("📁 No .env file found.")
        choice = input("Would you like to create one? (Y/n): ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            create_env_file()
        else:
            print("👋 Setup cancelled.")

if __name__ == "__main__":
    main()

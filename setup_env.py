#!/usr/bin/env python3
"""
Environment Setup Script for MLOps Pipeline
This script helps set up environment variables for GCP integration
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with GCP configuration"""
    env_content = """# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=./key.json
GCP_BUCKET_NAME=aya-internship-mlops-bucket
GCP_BUCKET_REGION=us-central1
ENABLE_GCP_UPLOAD=true

# API Configuration
API_BASE=http://localhost:8000

# Optional: Webhook Configuration
WEBHOOK_URL=https://requestcatcher.com/test

# Optional: Database Configuration
DATABASE_URL=sqlite:///mlops_pipeline.db

# Optional: Logging Configuration
LOG_LEVEL=INFO
"""
    
    # Check if .env already exists
    if Path(".env").exists():
        print("⚠️ .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled. .env file unchanged.")
            return False
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    return True

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking required packages...")
    
    required_packages = [
        "google-cloud-storage",
        "python-dotenv",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def check_gcp_files():
    """Check if GCP setup files exist"""
    print("\n🔍 Checking GCP setup files...")
    
    files_to_check = [
        ("key.json", "GCP service account credentials"),
        ("setup_gcp_bucket.py", "GCP bucket setup script"),
        ("GCP_BUCKET_SETUP.md", "GCP setup documentation")
    ]
    
    missing_files = []
    
    for filename, description in files_to_check:
        if Path(filename).exists():
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description}")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        print("Please run setup_gcp_bucket.py first to create GCP resources.")
        return False
    
    print("✅ All GCP setup files are present!")
    return True

def main():
    """Main setup function"""
    print("🚀 Environment Setup for MLOps Pipeline with GCP")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed due to missing packages.")
        return
    
    # Check GCP files
    if not check_gcp_files():
        print("\n⚠️ Some GCP files are missing, but setup can continue.")
    
    # Create .env file
    print("\n📝 Setting up environment variables...")
    if create_env_file():
        print("\n🎉 Environment setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Make sure you have GCP credentials in key.json")
        print("   2. Start the MLOps pipeline: docker-compose up")
        print("   3. Test GCP uploads: python test_gcp_uploads.py")
        print("   4. Or test with local script: python test_real_files.py")
        
        print("\n💡 Your files will now be automatically uploaded to Google Cloud Storage!")
        print("🌐 Access them at: https://console.cloud.google.com/storage/browser/aya-internship-mlops-bucket")
    else:
        print("\n❌ Environment setup failed.")

if __name__ == "__main__":
    main()

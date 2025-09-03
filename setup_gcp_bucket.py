#!/usr/bin/env python3
"""
GCP Bucket Setup Script for MLOps Pipeline
This script automates the creation and configuration of GCP storage bucket
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def check_gcloud_installed():
    """Check if Google Cloud CLI is installed"""
    stdout, stderr, returncode = run_command("gcloud --version", check=False)
    if returncode != 0:
        print("❌ Google Cloud CLI (gcloud) is not installed!")
        print("Please install it from: https://cloud.google.com/sdk/docs/install")
        return False
    print("✅ Google Cloud CLI is installed")
    return True

def check_gcloud_auth():
    """Check if user is authenticated with GCP"""
    stdout, stderr, returncode = run_command("gcloud auth list --filter=status:ACTIVE --format=value(account)", check=False)
    if returncode != 0 or not stdout:
        print("❌ Not authenticated with Google Cloud!")
        print("Please run: gcloud auth login")
        return False
    print(f"✅ Authenticated as: {stdout}")
    return True

def create_project(project_id, project_name):
    """Create a new GCP project"""
    print(f"🔧 Creating project: {project_id}")
    
    # Check if project already exists
    stdout, stderr, returncode = run_command(f"gcloud projects describe {project_id}", check=False)
    if returncode == 0:
        print(f"✅ Project {project_id} already exists")
        return True
    
    # Create new project
    stdout, stderr, returncode = run_command(f"gcloud projects create {project_id} --name='{project_name}'")
    if returncode != 0:
        print(f"❌ Failed to create project: {stderr}")
        return False
    
    print(f"✅ Project {project_id} created successfully")
    return True

def set_project(project_id):
    """Set the project as default"""
    print(f"🎯 Setting {project_id} as default project")
    stdout, stderr, returncode = run_command(f"gcloud config set project {project_id}")
    if returncode != 0:
        print(f"❌ Failed to set project: {stderr}")
        return False
    
    print(f"✅ Project {project_id} set as default")
    return True

def enable_apis(project_id):
    """Enable required GCP APIs"""
    print("🔌 Enabling required APIs...")
    
    apis = [
        "storage.googleapis.com",
        "cloudresourcemanager.googleapis.com"
    ]
    
    for api in apis:
        print(f"   Enabling {api}...")
        stdout, stderr, returncode = run_command(f"gcloud services enable {api} --project={project_id}")
        if returncode != 0:
            print(f"   ❌ Failed to enable {api}: {stderr}")
        else:
            print(f"   ✅ {api} enabled")
    
    return True

def create_bucket(bucket_name, region):
    """Create a GCP storage bucket"""
    print(f"🪣 Creating bucket: gs://{bucket_name}")
    
    # Check if bucket already exists
    stdout, stderr, returncode = run_command(f"gsutil ls gs://{bucket_name}", check=False)
    if returncode == 0:
        print(f"✅ Bucket gs://{bucket_name} already exists")
        return True
    
    # Create new bucket
    stdout, stderr, returncode = run_command(f"gsutil mb -l {region} gs://{bucket_name}")
    if returncode != 0:
        print(f"❌ Failed to create bucket: {stderr}")
        return False
    
    print(f"✅ Bucket gs://{bucket_name} created successfully")
    return True

def create_service_account(project_id, sa_name, sa_display_name):
    """Create a service account for the pipeline"""
    print(f"👤 Creating service account: {sa_name}")
    
    # Check if service account already exists
    stdout, stderr, returncode = run_command(f"gcloud iam service-accounts describe {sa_name}@{project_id}.iam.gserviceaccount.com", check=False)
    if returncode == 0:
        print(f"✅ Service account {sa_name} already exists")
        return f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    # Create new service account
    stdout, stderr, returncode = run_command(f"gcloud iam service-accounts create {sa_name} --display-name='{sa_display_name}'")
    if returncode != 0:
        print(f"❌ Failed to create service account: {stderr}")
        return None
    
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    print(f"✅ Service account {sa_email} created successfully")
    return sa_email

def grant_permissions(project_id, sa_email):
    """Grant necessary permissions to the service account"""
    print(f"🔐 Granting permissions to {sa_email}")
    
    # Grant Storage Admin role
    stdout, stderr, returncode = run_command(
        f'gcloud projects add-iam-policy-binding {project_id} '
        f'--member="serviceAccount:{sa_email}" '
        f'--role="roles/storage.admin"'
    )
    if returncode != 0:
        print(f"❌ Failed to grant storage admin role: {stderr}")
        return False
    
    print("✅ Storage Admin role granted successfully")
    return True

def create_service_account_key(project_id, sa_name):
    """Create and download service account key"""
    print(f"🔑 Creating service account key for {sa_name}")
    
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    # Check if key.json already exists
    if Path("key.json").exists():
        print("✅ key.json already exists")
        return True
    
    # Create new key
    stdout, stderr, returncode = run_command(f"gcloud iam service-accounts keys create key.json --iam-account={sa_email}")
    if returncode != 0:
        print(f"❌ Failed to create service account key: {stderr}")
        return False
    
    print("✅ Service account key created and saved as key.json")
    return True

def create_env_file():
    """Create .env file with GCP configuration"""
    print("📝 Creating .env file...")
    
    env_content = """# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=./key.json
GCP_BUCKET_NAME=aya-internship-mlops-bucket
GCP_BUCKET_REGION=us-central1
ENABLE_GCP_UPLOAD=true

# API Configuration
API_BASE=http://localhost:8000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")
    return True

def test_gcp_connection():
    """Test the GCP connection"""
    print("🧪 Testing GCP connection...")
    
    try:
        from google.cloud import storage
        
        # Set credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
        
        # Test connection
        client = storage.Client(project="aya-internship")
        bucket = client.bucket("aya-internship-mlops-bucket")
        
        # Try to list blobs (this will test authentication and bucket access)
        blobs = list(bucket.list_blobs(max_results=1))
        print("✅ GCP connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ GCP connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 GCP Bucket Setup for MLOps Pipeline")
    print("=" * 50)
    
    # Configuration
    project_id = "aya-internship"
    project_name = "AYA Internship MLOps"
    bucket_name = "aya-internship-mlops-bucket"
    region = "us-central1"
    sa_name = "mlops-pipeline"
    sa_display_name = "MLOps-Pipeline-Service-Account"
    
    # Check prerequisites
    if not check_gcloud_installed():
        sys.exit(1)
    
    if not check_gcloud_auth():
        sys.exit(1)
    
    print("\n📋 Setup Steps:")
    print("1. Creating GCP project")
    print("2. Enabling APIs")
    print("3. Creating storage bucket")
    print("4. Creating service account")
    print("5. Granting permissions")
    print("6. Creating service account key")
    print("7. Creating environment file")
    print("8. Testing connection")
    
    print("\n" + "=" * 50)
    
    # Execute setup steps
    steps = [
        ("Creating project", lambda: create_project(project_id, project_name)),
        ("Setting project", lambda: set_project(project_id)),
        ("Enabling APIs", lambda: enable_apis(project_id)),
        ("Creating bucket", lambda: create_bucket(bucket_name, region)),
        ("Creating service account", lambda: create_service_account(project_id, sa_name, sa_display_name)),
        ("Granting permissions", lambda: grant_permissions(project_id, f"{sa_name}@{project_id}.iam.gserviceaccount.com")),
        ("Creating service account key", lambda: create_service_account_key(project_id, sa_name)),
        ("Creating .env file", create_env_file),
        ("Testing connection", test_gcp_connection)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed!")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 GCP setup completed successfully!")
    print("\n📁 Files created:")
    print("   - key.json (service account credentials)")
    print("   - .env (environment configuration)")
    print("\n🚀 Next steps:")
    print("   1. Start the MLOps pipeline: docker-compose up")
    print("   2. Test GCP uploads: python test_gcp_uploads.py")
    print("   3. Upload your GeoTIFF files!")
    
    print("\n📚 For more information, see: GCP_BUCKET_SETUP.md")

if __name__ == "__main__":
    main()

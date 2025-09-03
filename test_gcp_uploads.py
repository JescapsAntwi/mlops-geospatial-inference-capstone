#!/usr/bin/env python3
"""
Test Script for GCP Uploads
This script tests the MLOps pipeline with GCP cloud storage integration

# 3. Start the pipeline
docker-compose up

# 4. Test GCP uploads
python test_gcp_uploads.py
"""

import os
import requests
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
load_dotenv()

# API base URL
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# GCP Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "aya-internship-mlops-bucket")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./key.json")

def check_gcp_credentials():
    """Check if GCP credentials are properly configured"""
    print("🔐 Checking GCP credentials...")
    
    if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        print(f"❌ Credentials file not found: {GOOGLE_APPLICATION_CREDENTIALS}")
        return False
    
    try:
        # Set credentials environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
        
        # Test GCP connection
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        # Try to access bucket
        bucket.reload()
        print(f"✅ GCP credentials valid - connected to bucket: gs://{GCP_BUCKET_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ GCP credentials invalid: {e}")
        return False

def list_gcp_bucket_contents():
    """List contents of the GCP bucket"""
    print(f"📋 Listing contents of gs://{GCP_BUCKET_NAME}...")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        blobs = list(bucket.list_blobs())
        
        if not blobs:
            print("   📁 Bucket is empty")
            return []
        
        print(f"   📁 Found {len(blobs)} objects:")
        for blob in blobs[:10]:  # Show first 10
            print(f"      - {blob.name} ({blob.size} bytes)")
        
        if len(blobs) > 10:
            print(f"      ... and {len(blobs) - 10} more objects")
        
        return blobs
        
    except Exception as e:
        print(f"❌ Failed to list bucket contents: {e}")
        return []

def upload_to_gcp_directly(file_path, blob_name):
    """Upload a file directly to GCP (for testing)"""
    print(f"☁️ Uploading {file_path} to GCP as {blob_name}...")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(blob_name)
        
        # Upload file
        blob.upload_from_filename(file_path)
        
        print(f"✅ Direct upload successful: gs://{GCP_BUCKET_NAME}/{blob_name}")
        return True
        
    except Exception as e:
        print(f"❌ Direct upload failed: {e}")
        return False

def test_upload_real_files():
    """Test uploading the real Juaben GeoTIFF files via API"""
    try:
        # List of GeoTIFF files to upload
        geotiff_files = [
            "Juaben_tile_0.tif",
            "Juaben_tile_1.tif", 
            "Juaben_tile_10.tif",
            "Juaben_tile_100.tif",
            "Juaben_tile_101.tif",
            "Juaben_tile_102.tif",
            "Juaben_tile_103.tif",
            "Juaben_tile_104.tif",
            "Juaben_tile_105.tif",
            "Juaben_tile_106.tif",
            "Juaben_tile_107.tif"
        ]
        
        # Check which files exist
        existing_files = []
        for file_name in geotiff_files:
            if Path(file_name).exists():
                existing_files.append(file_name)
                print(f"✅ Found: {file_name}")
            else:
                print(f"❌ Missing: {file_name}")
        
        if not existing_files:
            print("❌ No GeoTIFF files found to upload!")
            return None
        
        print(f"\n📤 Uploading {len(existing_files)} GeoTIFF files via API...")
        
        # Prepare files for upload
        files = []
        for file_name in existing_files:
            with open(file_name, 'rb') as f:
                files.append(('files', (file_name, f.read(), 'image/tiff')))
        
        # Test webhook URL (you can use requestcatcher.com for testing)
        webhook_url = "https://requestcatcher.com/test"  # Replace with your webhook URL
        
        data = {'webhook_url': webhook_url}
        
        # Upload files
        response = requests.post(
            f"{API_BASE}/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API upload successful!")
            print(f"📋 Job ID: {result['job_id']}")
            print(f"📊 Status: {result['status']}")
            print(f"💬 Message: {result['message']}")
            return result['job_id']
        else:
            print(f"❌ API upload failed with status {response.status_code}")
            print(f"📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during API upload: {e}")
        return None

def test_gcp_upload_verification(job_id):
    """Verify that files were uploaded to GCP after API upload"""
    print(f"🔍 Verifying GCP uploads for job {job_id}...")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        # Look for files with this job ID
        job_prefix = f"uploads/{job_id}_"
        blobs = list(bucket.list_blobs(prefix=job_prefix))
        
        if not blobs:
            print(f"❌ No files found in GCP for job {job_id}")
            return False
        
        print(f"✅ Found {len(blobs)} files in GCP for job {job_id}:")
        for blob in blobs:
            print(f"   📁 {blob.name} ({blob.size} bytes)")
            print(f"      📅 Created: {blob.time_created}")
            print(f"      🔗 URL: gs://{GCP_BUCKET_NAME}/{blob.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to verify GCP uploads: {e}")
        return False

def test_job_status(job_id):
    """Test job status checking"""
    try:
        print(f"🔍 Checking status for job {job_id}...")
        response = requests.get(f"{API_BASE}/status/{job_id}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Job Status:")
            print(f"   📊 Status: {status['status']}")
            print(f"   📈 Progress: {status['progress']}%")
            print(f"   📁 Files: {status['processed_files']}/{status['total_files']}")
            print(f"   🕐 Created: {status['created_at']}")
            print(f"   🔄 Updated: {status['updated_at']}")
            return status
        else:
            print(f"❌ Status check failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking job status: {e}")
        return None

def monitor_job_completion(job_id, max_wait_time=120):
    """Monitor a job until completion"""
    print(f"⏳ Monitoring job {job_id} for completion...")
    print(f"⏰ Maximum wait time: {max_wait_time} seconds")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        status = test_job_status(job_id)
        if status and status['status'] in ['completed', 'failed']:
            print(f"🎉 Job {job_id} completed with status: {status['status']}")
            return status
        
        print("⏳ Waiting 10 seconds before next check...")
        time.sleep(10)
    
    print(f"⏰ Timeout reached. Job may still be processing.")
    return None

def test_gcp_results_verification(job_id):
    """Verify that results were stored in GCP after job completion"""
    print(f"🔍 Verifying GCP results for job {job_id}...")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        # Look for result files with this job ID
        job_prefix = f"results/{job_id}_"
        blobs = list(bucket.list_blobs(prefix=job_prefix))
        
        if not blobs:
            print(f"❌ No result files found in GCP for job {job_id}")
            return False
        
        print(f"✅ Found {len(blobs)} result files in GCP for job {job_id}:")
        for blob in blobs:
            print(f"   📁 {blob.name} ({blob.size} bytes)")
            print(f"      📅 Created: {blob.time_created}")
            print(f"      🔗 URL: gs://{GCP_BUCKET_NAME}/{blob.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to verify GCP results: {e}")
        return False

def main():
    """Run the GCP upload tests"""
    print("🚀 Testing MLOps Pipeline with GCP Cloud Storage")
    print("=" * 60)
    
    # Test 1: Check GCP Credentials
    if not check_gcp_credentials():
        print("❌ GCP credentials check failed. Please run setup_gcp_bucket.py first.")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: List Current Bucket Contents
    list_gcp_bucket_contents()
    
    print("\n" + "=" * 60)
    
    # Test 3: Upload Real GeoTIFF Files via API
    job_id = test_upload_real_files()
    if not job_id:
        print("❌ File upload test failed. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Test 4: Verify GCP Uploads
    test_gcp_upload_verification(job_id)
    
    print("\n" + "=" * 60)
    
    # Test 5: Check Initial Job Status
    test_job_status(job_id)
    
    print("\n" + "=" * 60)
    
    # Test 6: Monitor Job Completion
    print("🔄 Monitoring job completion...")
    final_status = monitor_job_completion(job_id)
    
    if final_status and final_status['status'] == 'completed':
        print("\n🎉 All tests completed successfully!")
        print("📁 Check the GCP bucket for COCO format output files")
        print("🔔 Check your webhook endpoint for notifications")
        
        # Show results summary
        print("\n📊 Results Summary:")
        print(f"   📁 Total files processed: {final_status['total_files']}")
        print(f"   ✅ Successfully processed: {final_status['processed_files']}")
        print(f"   📈 Progress: {final_status['progress']}%")
        
        # Test 7: Verify GCP Results
        print("\n" + "=" * 60)
        test_gcp_results_verification(job_id)
        
    else:
        print("\n⚠️ Some tests may have failed or timed out")
    
    print("\n" + "=" * 60)
    
    # Final bucket status
    print("📋 Final GCP Bucket Status:")
    list_gcp_bucket_contents()
    
    print("\n" + "=" * 60)
    print("🏁 GCP test sequence completed")
    print("\n💡 Your GeoTIFF files are now stored in Google Cloud Storage!")
    print(f"🌐 Access them at: https://console.cloud.google.com/storage/browser/{GCP_BUCKET_NAME}")

if __name__ == "__main__":
    main()

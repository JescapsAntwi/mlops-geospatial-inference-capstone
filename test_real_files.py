"""
Test Script for Real GeoTIFF Files
This script tests the MLOps pipeline with the actual Juaben GeoTIFF tiles
"""

import requests
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/upload")

# GCP Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "aya-internship-mlops-bucket")
ENABLE_GCP_UPLOAD = os.getenv("ENABLE_GCP_UPLOAD", "true").lower() in ("1","true","yes")

# def test_upload_real_files():
#     """Test uploading the real Juaben GeoTIFF files"""
#     try:
#         # List of GeoTIFF files to upload
#         geotiff_files = [
#             "Juaben_tile_0.tif",
#             "Juaben_tile_1.tif", 
#             "Juaben_tile_10.tif",
#             "Juaben_tile_100.tif",
#             "Juaben_tile_101.tif",
#             "Juaben_tile_102.tif",
#             "Juaben_tile_103.tif",
#             "Juaben_tile_104.tif",
#             "Juaben_tile_105.tif",
#             "Juaben_tile_106.tif",
#             "Juaben_tile_107.tif"
#         ]
        
#         # Check which files exist
#         files = []
#         for file_name in geotiff_files:
#             if Path(file_name).exists():
#                 files.append(file_name)
#                 print(f"✅ Found: {file_name}")
#             else:
#                 print(f"❌ Missing: {file_name}")
        
#         # if not existing_files:
#         #     print("❌ No GeoTIFF files found to upload!")
#         #     return None
        
#         print(f"\n📤 Uploading {len(files)} GeoTIFF files...")
        
#         # Prepare files for upload
#         files = []
#         for file_name in files:
#             with open(file_name, 'rb') as f:
#                 files.append(('files', (file_name, f.read(), 'image/tiff')))
        
#         # Test webhook URL (you can use requestcatcher.com for testing)
#         webhook_url = "https://requestcatcher.com/test"  # Replace with your webhook URL
        
#         data = {'webhook_url': webhook_url}
        
#         # Upload files
#         response = requests.post(
#             f"{API_BASE}/uploads",
#             files=files,
#             data=data
#         )
        
#         if response.status_code == 200:
#             result = response.json()
#             print(f"✅ Upload successful!")
#             print(f"📋 Job ID: {result['job_id']}")
#             print(f"📊 Status: {result['status']}")
#             print(f"💬 Message: {result['message']}")
#             return result['job_id']
#         else:
#             print(f"❌ Upload failed with status {response.status_code}")
#             print(f"📝 Response: {response.text}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error during upload: {e}")
#         return None

def test_upload_real_files():
    # Local test files (replace with real paths)
    file_paths = [
        "Juaben_tile_0.tif",
        "Juaben_tile_10.tif",
        "Juaben_tile_10.tif",
        "Juaben_tile_101.tif"
    ]

    # Optional webhook URL
    webhook_url = "http://example.com/webhook"

    # Prepare files for multipart/form-data
    files = [
        ("files", (open(path, "rb").name, open(path, "rb"), "application/octet-stream"))
        for path in file_paths
    ]

    # Form data
    data = {
        "webhook_url": webhook_url
    }
    try:
        response = requests.post(API_BASE, files=files, data=data, timeout=60)

        print(f"Status Code: {response.status_code}")

        try:
            print("Response JSON:")
            print(response.json())
        except Exception:
            print("Response Text:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    finally:
        # Close file handles
        for _, (filename, file_obj, _) in files:
            file_obj.close()


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

def check_gcp_status():
    """Check GCP configuration status"""
    print("☁️ Checking GCP Configuration...")
    print(f"   📦 Bucket: {GCP_BUCKET_NAME}")
    print(f"   🔧 GCP Uploads: {'✅ Enabled' if ENABLE_GCP_UPLOAD else '❌ Disabled'}")
    
    if ENABLE_GCP_UPLOAD:
        print("   💡 Files will be uploaded to Google Cloud Storage")
        print(f"   🌐 Bucket URL: https://console.cloud.google.com/storage/browser/{GCP_BUCKET_NAME}")
    else:
        print("   💡 Files will be stored locally only")
    
    print()

def main():
    """Run the test with real GeoTIFF files"""
    print("🚀 Testing MLOps Pipeline with Real GeoTIFF Files")
    print("=" * 60)
    
    # Check GCP status
    check_gcp_status()
    
    # Test 1: Upload Real GeoTIFF Files
    job_id = test_upload_real_files()
    if not job_id:
        print("❌ File upload test failed. Exiting.")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Check Initial Job Status
    test_job_status(job_id)
    
    print("\n" + "=" * 60)
    
    # Test 3: Monitor Job Completion
    print("🔄 Monitoring job completion...")
    final_status = monitor_job_completion(job_id)
    
    if final_status and final_status['status'] == 'completed':
        print("\n🎉 All tests completed successfully!")
        print("📁 Check the 'results' folder for COCO format output files")
        print("🔔 Check your webhook endpoint for notifications")
        
        # Show results summary
        print("\n📊 Results Summary:")
        print(f"   📁 Total files processed: {final_status['total_files']}")
        print(f"   ✅ Successfully processed: {final_status['processed_files']}")
        print(f"   📈 Progress: {final_status['progress']}%")
        
    else:
        print("\n⚠️ Some tests may have failed or timed out")
    
    print("\n" + "=" * 60)
    
    if ENABLE_GCP_UPLOAD:
        print("☁️ GCP Storage Summary:")
        print(f"   📦 Your GeoTIFF files are now stored in Google Cloud Storage!")
        print(f"   🌐 Access them at: https://console.cloud.google.com/storage/browser/{GCP_BUCKET_NAME}")
        print("   💡 Benefits of GCP storage:")
        print("      - Scalable and reliable cloud storage")
        print("      - Easy access from anywhere")
        print("      - Built-in redundancy and backup")
        print("      - Cost-effective for large datasets")
    
    print("\n" + "=" * 60)
    print("🏁 Test sequence completed")

if __name__ == "__main__":
    main()
"""
Test Script for Real GeoTIFF Files
This script tests the MLOps pipeline with the actual Juaben GeoTIFF tiles
"""

import requests
import json
import time
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000"

def test_upload_real_files():
    """Test uploading the real Juaben GeoTIFF files"""
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
        
        print(f"\n📤 Uploading {len(existing_files)} GeoTIFF files...")
        
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
            print(f"✅ Upload successful!")
            print(f"📋 Job ID: {result['job_id']}")
            print(f"📊 Status: {result['status']}")
            print(f"💬 Message: {result['message']}")
            return result['job_id']
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return None

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

def main():
    """Run the test with real GeoTIFF files"""
    print("🚀 Testing MLOps Pipeline with Real GeoTIFF Files")
    print("=" * 60)
    
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
    print("🏁 Test sequence completed")

if __name__ == "__main__":
    main()

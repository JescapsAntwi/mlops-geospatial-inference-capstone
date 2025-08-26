"""
Test Script for MLOps Pipeline
This script demonstrates the complete pipeline functionality
"""

import asyncio
import requests
import json
import time
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            print(f"📋 API Info: {response.json()}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on port 8000")
        return False

def create_sample_geotiff():
    """Create a sample GeoTIFF file for testing"""
    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_bounds
        
        # Create a simple test image
        height, width = 256, 256
        image = np.random.randint(0, 255, (height, width), dtype=np.uint8)
        
        # Define bounds (simple example)
        bounds = (0, 0, 1000, 1000)
        transform = from_bounds(*bounds, width, height)
        
        # Save as GeoTIFF
        output_path = "test_sample.tif"
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=image.dtype,
            crs='EPSG:4326',
            transform=transform
        ) as dst:
            dst.write(image, 1)
        
        print(f"✅ Created sample GeoTIFF: {output_path}")
        return output_path
        
    except ImportError:
        print("⚠️ Rasterio not available, using dummy file")
        # Create a dummy file if rasterio is not available
        dummy_path = "test_sample.tif"
        with open(dummy_path, 'wb') as f:
            f.write(b"DUMMY_GEOTIFF_CONTENT")
        return dummy_path

def test_upload_files():
    """Test file upload functionality"""
    try:
        # Create sample files
        sample_file = create_sample_geotiff()
        
        # Prepare files for upload
        files = [
            ('files', ('sample1.tif', open(sample_file, 'rb'), 'image/tiff')),
            ('files', ('sample2.tif', open(sample_file, 'rb'), 'image/tiff')),
        ]
        
        # Test webhook URL (you can use requestcatcher.com for testing)
        webhook_url = "https://requestcatcher.com/test"  # Replace with your webhook URL
        
        data = {'webhook_url': webhook_url}
        
        print("📤 Uploading test files...")
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
        print(f"❌ Error during upload test: {e}")
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

def test_list_jobs():
    """Test listing all jobs"""
    try:
        print("📋 Listing all jobs...")
        response = requests.get(f"{API_BASE}/jobs")
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Found {len(jobs['jobs'])} jobs:")
            for job in jobs['jobs']:
                print(f"   🆔 {job['job_id']}: {status['status']} ({status['progress']}%)")
            return jobs
        else:
            print(f"❌ Failed to list jobs with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error listing jobs: {e}")
        return None

def monitor_job_completion(job_id, max_wait_time=60):
    """Monitor a job until completion"""
    print(f"⏳ Monitoring job {job_id} for completion...")
    print(f"⏰ Maximum wait time: {max_wait_time} seconds")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        status = test_job_status(job_id)
        if status and status['status'] in ['completed', 'failed']:
            print(f"🎉 Job {job_id} completed with status: {status['status']}")
            return status
        
        print("⏳ Waiting 5 seconds before next check...")
        time.sleep(5)
    
    print(f"⏰ Timeout reached. Job may still be processing.")
    return None

def main():
    """Run all tests"""
    print("🚀 Starting MLOps Pipeline Tests")
    print("=" * 50)
    
    # Test 1: API Health
    if not test_api_health():
        print("❌ API health check failed. Exiting.")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Upload Files
    job_id = test_upload_files()
    if not job_id:
        print("❌ File upload test failed. Exiting.")
        return
    
    print("\n" + "=" * 50)
    
    # Test 3: Check Job Status
    test_job_status(job_id)
    
    print("\n" + "=" * 50)
    
    # Test 4: List All Jobs
    test_list_jobs()
    
    print("\n" + "=" * 50)
    
    # Test 5: Monitor Job Completion
    print("🔄 Monitoring job completion...")
    final_status = monitor_job_completion(job_id)
    
    if final_status and final_status['status'] == 'completed':
        print("\n🎉 All tests completed successfully!")
        print("📁 Check the 'results' folder for COCO format output files")
        print("🔔 Check your webhook endpoint for notifications")
    else:
        print("\n⚠️ Some tests may have failed or timed out")
    
    print("\n" + "=" * 50)
    print("🏁 Test sequence completed")

if __name__ == "__main__":
    main()

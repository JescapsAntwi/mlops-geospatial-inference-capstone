#!/usr/bin/env python3
"""
Direct GCP Upload Test
This script tests direct upload to GCP to verify credentials and bucket access
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
load_dotenv()

def test_direct_gcp_upload():
    """Test direct upload to GCP"""
    print("🧪 Testing Direct GCP Upload")
    print("=" * 40)
    
    # Check environment
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"📦 Bucket: {bucket_name}")
    print(f"🔑 Credentials: {creds_file}")
    print()
    
    # Test GCP connection
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Test bucket access
        bucket.reload()
        print("✅ GCP connection successful")
        print(f"✅ Bucket {bucket_name} accessible")
        
        # List current contents
        blobs = list(bucket.list_blobs())
        print(f"📁 Current bucket contents: {len(blobs)} objects")
        
        # Test upload with a small file
        test_file = "test_gcp_upload.txt"
        test_content = "This is a test file for GCP upload verification"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        print(f"📝 Created test file: {test_file}")
        
        # Upload to GCP
        blob_name = f"test/{test_file}"
        blob = bucket.blob(blob_name)
        
        print(f"☁️ Uploading {test_file} to gs://{bucket_name}/{blob_name}")
        blob.upload_from_filename(test_file)
        
        print("✅ Upload successful!")
        
        # Verify upload
        blob.reload()
        print(f"📊 File size: {blob.size} bytes")
        print(f"📅 Created: {blob.time_created}")
        
        # Clean up local test file
        os.remove(test_file)
        print(f"🧹 Cleaned up local test file")
        
        # List updated contents
        blobs = list(bucket.list_blobs())
        print(f"📁 Updated bucket contents: {len(blobs)} objects")
        
        return True
        
    except Exception as e:
        print(f"❌ GCP test failed: {e}")
        return False

def test_upload_existing_files():
    """Test uploading existing GeoTIFF files to GCP"""
    print("\n🧪 Testing Upload of Existing GeoTIFF Files")
    print("=" * 40)
    
    try:
        bucket_name = os.getenv("GCP_BUCKET_NAME")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Find some GeoTIFF files
        geotiff_files = list(Path(".").glob("Juaben_tile_*.tif"))[:3]  # Just test first 3
        
        if not geotiff_files:
            print("❌ No GeoTIFF files found")
            return False
        
        print(f"📁 Found {len(geotiff_files)} GeoTIFF files to test")
        
        for file_path in geotiff_files:
            try:
                # Upload to GCP
                blob_name = f"test_uploads/{file_path.name}"
                blob = bucket.blob(blob_name)
                
                print(f"☁️ Uploading {file_path.name} to gs://{bucket_name}/{blob_name}")
                blob.upload_from_filename(str(file_path))
                
                print(f"✅ {file_path.name} uploaded successfully!")
                
            except Exception as e:
                print(f"❌ Failed to upload {file_path.name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ GeoTIFF upload test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Direct GCP Upload Test")
    print("=" * 50)
    
    # Test 1: Basic GCP connection and small file upload
    if test_direct_gcp_upload():
        print("\n✅ Basic GCP test passed!")
    else:
        print("\n❌ Basic GCP test failed!")
        return
    
    # Test 2: Upload existing GeoTIFF files
    if test_upload_existing_files():
        print("\n✅ GeoTIFF upload test passed!")
    else:
        print("\n❌ GeoTIFF upload test failed!")
    
    print("\n" + "=" * 50)
    print("🏁 Direct GCP upload test completed")

if __name__ == "__main__":
    main()

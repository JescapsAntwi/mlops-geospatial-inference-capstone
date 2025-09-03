# MLOps Pipeline with Google Cloud Platform (GCP) Integration

This document explains how to use the MLOps pipeline with Google Cloud Storage for scalable, cloud-based image processing.

## 🚀 Quick Start

### 1. Automatic Setup (Recommended)

```bash
# Run the automated GCP setup
python setup_gcp_bucket.py

# Set up environment variables
python setup_env.py

# Start the pipeline
docker-compose up

# Test GCP uploads
python test_gcp_uploads.py
```

### 2. Manual Setup

If you prefer to set up GCP manually, follow the detailed instructions in [GCP_BUCKET_SETUP.md](GCP_BUCKET_SETUP.md).

## ☁️ GCP Features

### Automatic Cloud Storage

- **Dual Storage**: Files are saved locally AND uploaded to GCP
- **Scalable**: Handle thousands of GeoTIFF files
- **Reliable**: Built-in redundancy and backup
- **Cost-effective**: Pay only for what you use

### Smart File Management

- **Organized Structure**: Files are organized by job ID
- **Metadata Tracking**: Full audit trail of uploads and processing
- **Easy Access**: Access files from anywhere via GCP Console

### Processing Pipeline

- **Cloud Processing**: ML inference runs locally, results stored in cloud
- **Webhook Notifications**: Get notified when processing completes
- **Progress Tracking**: Monitor job status in real-time

## 📁 File Organization

```
gs://aya-internship-mlops-bucket/
├── uploads/                    # Original GeoTIFF files
│   ├── {job_id}_file1.tif
│   └── {job_id}_file2.tif
├── results/                    # Processed COCO format files
│   ├── {job_id}_coco.json
│   └── {job_id}_metadata.json
└── temp/                       # Temporary processing files
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (or use `config.env` as a template):

```bash
# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=./key.json
GCP_BUCKET_NAME=aya-internship-mlops-bucket
GCP_BUCKET_REGION=us-central1
ENABLE_GCP_UPLOAD=true

# API Configuration
API_BASE=http://localhost:8000
```

### Docker Configuration

The `docker-compose.yml` is already configured for GCP:

```yaml
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/app/key.json
  - GCP_BUCKET_NAME=aya-internship-mlops-bucket
  - GCP_BUCKET_REGION=us-central1
```

## 📊 Usage Examples

### Upload GeoTIFF Files

```python
import requests

# Upload multiple GeoTIFF files
files = [
    ('files', ('image1.tif', open('image1.tif', 'rb'), 'image/tiff')),
    ('files', ('image2.tif', open('image2.tif', 'rb'), 'image/tiff'))
]

response = requests.post(
    'http://localhost:8000/upload',
    files=files,
    data={'webhook_url': 'https://your-webhook.com/notify'}
)

job_id = response.json()['job_id']
print(f"Job created: {job_id}")
```

### Check Job Status

```python
# Check processing status
status_response = requests.get(f'http://localhost:8000/status/{job_id}')
status = status_response.json()

print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"Files: {status['processed_files']}/{status['total_files']}")
```

### Access GCP Files

```python
from google.cloud import storage

# List files in GCP bucket
client = storage.Client()
bucket = client.bucket('aya-internship-mlops-bucket')

# List all files
blobs = bucket.list_blobs()
for blob in blobs:
    print(f"File: {blob.name}, Size: {blob.size} bytes")

# Download a specific file
blob = bucket.blob('uploads/job123_image.tif')
blob.download_to_filename('downloaded_image.tif')
```

## 🧪 Testing

### Test GCP Integration

```bash
# Test GCP uploads and processing
python test_gcp_uploads.py

# Test with local script (also uploads to GCP)
python test_real_files.py

# Test environment setup
python setup_env.py
```

### Test Results

After running tests, you should see:

- ✅ Files uploaded to GCP bucket
- ✅ Processing completed successfully
- ✅ Results stored in GCP
- ✅ Webhook notifications sent

## 🔍 Monitoring and Debugging

### Check GCP Bucket Contents

```bash
# List bucket contents
gsutil ls gs://aya-internship-mlops-bucket/

# Check specific job files
gsutil ls gs://aya-internship-mlops-bucket/uploads/job_id_*

# View bucket details
gsutil bucket-info gs://aya-internship-mlops-bucket
```

### Check Application Logs

```bash
# View Docker logs
docker-compose logs mlops-api

# View specific service logs
docker-compose logs inference-worker
```

### Common Issues and Solutions

| Issue                 | Solution                                            |
| --------------------- | --------------------------------------------------- |
| Authentication failed | Check `key.json` exists and has correct permissions |
| Bucket not found      | Verify bucket name in `.env` file                   |
| Upload timeout        | Check network connection and file size              |
| Processing failed     | Check ML model files and dependencies               |

## 💰 Cost Optimization

### Storage Costs

- **Standard Storage**: ~$0.02 per GB per month
- **Nearline Storage**: ~$0.01 per GB per month (for archival)
- **Coldline Storage**: ~$0.004 per GB per month (for long-term storage)

### Network Costs

- **Ingress**: Free (uploading to GCP)
- **Egress**: ~$0.12 per GB (downloading from GCP)

### Recommendations

1. **Use Standard Storage** for active processing
2. **Move to Nearline** after 30 days
3. **Archive to Coldline** after 90 days
4. **Enable lifecycle management** for automatic cost optimization

## 🔒 Security Best Practices

### Service Account Security

- Use dedicated service account with minimal permissions
- Rotate keys regularly
- Monitor access logs

### Data Security

- Enable default encryption
- Use IAM policies for access control
- Enable audit logging

### Network Security

- Use VPC for private access
- Enable Cloud Armor for DDoS protection
- Use HTTPS for all API calls

## 🚀 Scaling and Performance

### Horizontal Scaling

- Run multiple inference workers
- Use Redis for job queuing
- Implement load balancing

### Performance Optimization

- Use Cloud CDN for global access
- Enable compression for large files
- Use parallel processing for multiple files

### Monitoring

- Set up Cloud Monitoring alerts
- Track processing times and throughput
- Monitor storage usage and costs

## 📚 Additional Resources

- [GCP Storage Documentation](https://cloud.google.com/storage/docs)
- [GCP IAM Best Practices](https://cloud.google.com/iam/docs/best-practices)
- [GCP Cost Optimization](https://cloud.google.com/storage/docs/cost-optimization)
- [MLOps Pipeline Documentation](README.md)

## 🤝 Support

If you encounter issues:

1. Check the [GCP_BUCKET_SETUP.md](GCP_BUCKET_SETUP.md) troubleshooting section
2. Verify your `.env` configuration
3. Check GCP Console for bucket and service account status
4. Review application logs for error details

## 🎯 Next Steps

After setting up GCP integration:

1. **Process Large Datasets**: Upload thousands of GeoTIFF files
2. **Implement Cloud ML**: Move ML inference to Google Cloud AI
3. **Set Up Monitoring**: Configure alerts and dashboards
4. **Optimize Costs**: Implement lifecycle management policies
5. **Scale Globally**: Deploy to multiple regions for better performance

---

**Happy Cloud Processing! ☁️🚀**

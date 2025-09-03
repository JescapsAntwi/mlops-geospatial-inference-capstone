# GCP Bucket Setup for MLOps Pipeline

This document explains how to set up Google Cloud Platform (GCP) for storing and processing GeoTIFF images in the MLOps pipeline.

## Prerequisites

1. **Google Cloud Account**: You need a GCP account with billing enabled
2. **Google Cloud SDK**: Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
3. **Python Dependencies**: The required packages are already in `requirements.txt`

## Step 1: Create a GCP Project

```bash
# Create a new project (or use existing)
gcloud projects create aya-internship --name="AYA Internship MLOps"

# Set the project as default
gcloud config set project aya-internship

# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

## Step 2: Create a Storage Bucket

```bash
# Create a bucket in us-central1 (or your preferred region)
gsutil mb -l us-central1 gs://aya-internship-mlops-bucket

# Make the bucket publicly readable (optional, for testing)
gsutil iam ch allUsers:objectViewer gs://aya-internship-mlops-bucket
```

## Step 3: Create Service Account

```bash
# Create a service account
gcloud iam service-accounts create mlops-pipeline \
    --display-name="MLOps Pipeline Service Account"

# Get the service account email
SA_EMAIL=$(gcloud iam service-accounts list \
    --filter="displayName:MLOps Pipeline Service Account" \
    --format="value(email)")

# Grant Storage Admin role
gcloud projects add-iam-policy-binding aya-internship \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

# Create and download the key
gcloud iam service-accounts keys create key.json \
    --iam-account=$SA_EMAIL
```

## Step 4: Configure Environment Variables

Create a `.env` file in your project root:

```bash
# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=./key.json
GCP_BUCKET_NAME=aya-internship-mlops-bucket
GCP_BUCKET_REGION=us-central1
ENABLE_GCP_UPLOAD=true

# API Configuration
API_BASE=http://localhost:8000
```

## Step 5: Test GCP Connection

Run the test script to verify GCP integration:

```bash
python test_gcp_uploads.py
```

## Step 6: Upload Images to GCP

The pipeline will automatically:
1. Save uploaded GeoTIFF files locally
2. Upload them to GCP bucket
3. Process them using the ML model
4. Store results in GCP

## Bucket Structure

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

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure `key.json` is in the project root and has correct permissions
2. **Bucket Not Found**: Verify bucket name and region match your configuration
3. **Permission Denied**: Check service account has Storage Admin role
4. **Quota Exceeded**: Check GCP quotas for your project

### Debug Commands

```bash
# Test GCP authentication
gcloud auth list

# Check bucket contents
gsutil ls gs://aya-internship-mlops-bucket/

# View bucket details
gsutil bucket-info gs://aya-internship-mlops-bucket

# Check service account permissions
gcloud projects get-iam-policy aya-internship
```

## Cost Considerations

- **Storage**: ~$0.02 per GB per month
- **Network**: ~$0.12 per GB (outbound)
- **Processing**: Free tier includes 5GB storage and 1GB network

## Security Best Practices

1. **Service Account**: Use dedicated service account with minimal permissions
2. **Bucket Policies**: Configure appropriate IAM policies
3. **Encryption**: Enable default encryption for your bucket
4. **Access Logs**: Enable access logging for audit purposes
5. **Versioning**: Consider enabling object versioning for data protection

## Next Steps

After setup, you can:
1. Run the full pipeline with GCP storage
2. Scale processing across multiple workers
3. Implement cloud-based ML inference
4. Set up automated backups and archiving

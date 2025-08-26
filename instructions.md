# MLOps Pipeline - Setup and Running Instructions

## 🚀 Quick Start Guide

This guide will help you set up and run the MLOps Pipeline for Geospatial Inference. The system processes GeoTIFF images using a simulated Palm model and outputs results in COCO format.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

### Required Software

- **Python 3.11+** - Download from [python.org](https://python.org)
- **Docker Desktop** - Download from [docker.com](https://docker.com)
- **Git** - For cloning the repository

### System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 2GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux

## 🛠️ Installation Steps

### Step 1: Clone/Download the Project

```bash
# If using Git
git clone <repository-url>
cd capstone_project

# Or simply download and extract the ZIP file
```

### Step 2: Install Python Dependencies

```bash
# Navigate to the project directory
cd capstone_project

# Install required packages
pip install -r requirements.txt
```

**Note**: If you encounter issues with `rasterio` installation on Windows, you may need to install it from a wheel file:

```bash
# For Windows users having rasterio issues
pip install --only-binary=all rasterio
```

### Step 3: Verify Docker Installation

```bash
# Check if Docker is running
docker --version
docker-compose --version
```

Make sure Docker Desktop is running on your system.

## 🚀 Running the Pipeline

### Option 1: Run with Docker (Recommended)

This is the easiest way to run the entire system:

```bash
# Build and start the services
docker-compose up --build

# The API will be available at http://localhost:8000
```

### Option 2: Run Locally (Development)

If you prefer to run without Docker:

```bash
# Start the FastAPI server
python app.py

# The API will be available at http://localhost:8000
```

## 🧪 Testing the System

### 1. Test API Health

Open your browser and go to: `http://localhost:8000/`

You should see the API information and available endpoints.

### 2. Run the Test Script

```bash
# In a new terminal window
python test_pipeline.py
```

This script will:

- Create sample GeoTIFF files
- Upload them to the API
- Monitor processing progress
- Show results

### 3. Manual Testing with API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation where you can:

- Test all endpoints
- Upload files manually
- Check job statuses

## 📁 Understanding the Project Structure

```
capstone_project/
├── app.py                 # Main FastAPI application
├── database.py            # Database management (SQLite)
├── inference_worker.py    # Palm model simulation
├── post_processor.py      # COCO format conversion
├── webhook_sender.py      # Webhook notifications
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service setup
├── test_pipeline.py      # Test script
├── uploads/              # Uploaded GeoTIFF files
├── results/              # COCO output files
└── temp/                 # Temporary files
```

## 🔧 Configuration Options

### Environment Variables

You can customize the system by setting these environment variables:

```bash
# Database settings
DATABASE_PATH=mlops_pipeline.db

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# Webhook settings
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=5.0
```

### Webhook Configuration

To test webhook functionality:

1. **Use RequestCatcher** (free service):

   - Go to [requestcatcher.com](https://requestcatcher.com)
   - Create a new endpoint
   - Use the provided URL as your webhook URL

2. **Use ngrok** (for local testing):

   ```bash
   # Install ngrok
   pip install pyngrok

   # Create tunnel to your local server
   ngrok http 8000
   ```

## 📊 Monitoring and Debugging

### View Logs

```bash
# If using Docker
docker-compose logs -f mlops-api

# If running locally, logs appear in the terminal
```

### Check Database

The system uses SQLite by default. You can inspect it:

```bash
# Install SQLite browser or use command line
sqlite3 mlops_pipeline.db
.tables
SELECT * FROM jobs;
```

### API Endpoints

- `GET /` - API information
- `POST /upload` - Upload GeoTIFF files
- `GET /status/{job_id}` - Check job status
- `GET /jobs` - List all jobs
- `GET /docs` - Interactive API documentation

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

```bash
# Error: Address already in use
# Solution: Change port in docker-compose.yml or app.py
```

#### 2. Docker Build Fails

```bash
# Error: GDAL installation issues
# Solution: Ensure Docker has enough memory (4GB+) and try:
docker-compose build --no-cache
```

#### 3. Python Import Errors

```bash
# Error: Module not found
# Solution: Ensure you're in the correct directory and run:
pip install -r requirements.txt
```

#### 4. File Upload Issues

```bash
# Error: File validation fails
# Solution: Ensure files have .tif or .tiff extensions
```

#### 5. Webhook Delivery Fails

```bash
# Error: Webhook timeout
# Solution: Check webhook URL validity and network connectivity
```

### Performance Optimization

For processing large numbers of files:

1. **Increase Docker resources**:

   - Memory: 8GB+
   - CPU: 4+ cores

2. **Use batch processing**:

   - Upload files in smaller batches
   - Monitor system resources

3. **Database optimization**:
   - Consider switching to PostgreSQL for production
   - Add database indexes

## 🔒 Security Considerations

### Production Deployment

Before deploying to production:

1. **Add Authentication**:

   - Implement API key validation
   - Add JWT token support

2. **Secure File Uploads**:

   - Validate file types and sizes
   - Implement virus scanning

3. **Database Security**:

   - Use strong passwords
   - Enable SSL connections

4. **Network Security**:
   - Use HTTPS
   - Implement rate limiting
   - Add firewall rules

## 📈 Scaling the System

### Horizontal Scaling

```bash
# Scale API instances
docker-compose up --scale mlops-api=3

# Add load balancer (nginx)
# Use Kubernetes for orchestration
```

### Cloud Deployment

The system is designed to be easily deployable to cloud platforms:

- **AWS**: Use ECS or EKS
- **GCP**: Use Cloud Run or GKE
- **Azure**: Use AKS or Container Instances

## 📞 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify prerequisites** are installed correctly
3. **Test individual components** step by step
4. **Check the API documentation** at `/docs`

## 🎯 Next Steps

After successfully running the system:

1. **Test with real GeoTIFF files**
2. **Integrate actual Palm model** (replace simulation)
3. **Add monitoring and alerting**
4. **Implement production database**
5. **Add user authentication**
6. **Deploy to cloud infrastructure**

## 📝 License

This project is for educational purposes. Ensure you have proper licenses for any commercial use of the Palm model or other components.

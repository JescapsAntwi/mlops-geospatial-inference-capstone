# 🚀 MLOps Pipeline for Geospatial Inference

A complete, production-ready MLOps pipeline that processes GeoTIFF satellite images using the Palm model and delivers results in COCO format with automatic webhook notifications.

## 🎯 What This Project Does

This system is designed to handle the complete workflow for processing large numbers of GeoTIFF images:

1. **📤 Bulk Upload**: Accept 1,000+ GeoTIFF files through a REST API
2. **🧠 AI Processing**: Run inference using the Palm model (simulated for demo)
3. **📊 Format Conversion**: Convert results to industry-standard COCO JSON format
4. **🔔 Automatic Notifications**: Send webhook notifications when processing completes
5. **📈 Progress Tracking**: Real-time monitoring of processing status

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   FastAPI       │    │   Processing    │
│   Upload        │───▶│   Server        │───▶│   Pipeline      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SQLite        │    │   COCO          │
                       │   Database      │    │   Results       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Job Status    │    │   Webhook       │
                       │   Tracking      │    │   Notifications │
                       └─────────────────┘    └─────────────────┘
```

## ✨ Key Features

- **🚀 Scalable**: Handles 1,000+ images efficiently
- **🐳 Containerized**: Full Docker support for easy deployment
- **📊 Real-time Monitoring**: Live progress tracking and status updates
- **🔔 Webhook Integration**: Automatic notifications when jobs complete
- **📁 COCO Format**: Industry-standard output format
- **🔄 Fault Tolerant**: Continues processing even if individual files fail
- **📱 REST API**: Easy integration with existing systems

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Containerization**: Docker & Docker Compose
- **Geospatial**: Rasterio for GeoTIFF processing
- **Image Processing**: PIL/Pillow
- **Async Processing**: Python asyncio for non-blocking operations

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker Desktop
- 4GB+ RAM

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd capstone_project

# Start the system
docker-compose up --build

# Access the API at http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Access the API at http://localhost:8000
```

## 📖 Documentation

- **[📋 Instructions.md](instructions.md)** - Detailed setup and running instructions
- **[🎯 Explanation.md](explanation.md)** - Client-friendly project explanation
- **[📚 API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🧪 Testing

Run the complete test suite:

```bash
python test_pipeline.py
```

This will:

- Create sample GeoTIFF files
- Upload them to the API
- Monitor processing progress
- Verify COCO output format
- Test webhook functionality

## 📁 Project Structure

```
capstone_project/
├── 📄 app.py                 # Main FastAPI application
├── 🗄️ database.py            # Database management
├── 🤖 inference_worker.py    # AI model processing
├── 📊 post_processor.py      # COCO format conversion
├── 🔔 webhook_sender.py      # Notification system
├── 📦 requirements.txt       # Python dependencies
├── 🐳 Dockerfile            # Container configuration
├── 🚀 docker-compose.yml    # Multi-service setup
├── 🧪 test_pipeline.py      # Test automation
├── 📁 uploads/              # Uploaded GeoTIFF files
├── 📁 results/              # COCO output files
└── 📁 temp/                 # Temporary files
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_PATH=mlops_pipeline.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Webhook
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=5.0
```

### Webhook Testing

For testing webhook functionality:

- Use [RequestCatcher](https://requestcatcher.com) (free service)
- Or use ngrok for local testing

## 📊 API Endpoints

| Endpoint           | Method | Description                         |
| ------------------ | ------ | ----------------------------------- |
| `/`                | GET    | API information and health check    |
| `/upload`          | POST   | Upload GeoTIFF files for processing |
| `/status/{job_id}` | GET    | Check job processing status         |
| `/jobs`            | GET    | List all jobs                       |
| `/docs`            | GET    | Interactive API documentation       |

## 🔄 Processing Workflow

1. **Upload**: Client uploads GeoTIFF files via API
2. **Validation**: System validates file format and creates job
3. **Processing**: Background task processes each image through Palm model
4. **Conversion**: Results converted to COCO format
5. **Storage**: COCO results saved to disk
6. **Notification**: Webhook sent to client with results summary
7. **Completion**: Job marked as complete with full results

## 🌐 Cloud Deployment

The system is designed to be easily deployable to cloud platforms:

- **AWS**: ECS, EKS, or Lambda
- **Google Cloud**: Cloud Run, GKE, or Compute Engine
- **Azure**: AKS, Container Instances, or Functions

### Migration Path

1. **Current**: Local development with Docker
2. **Next**: Cloud storage integration (S3, Cloud Storage)
3. **Production**: Full cloud deployment with auto-scaling

## 🔒 Security Features

- File type validation (GeoTIFF only)
- Secure file handling
- Ready for API key authentication
- Prepared for JWT implementation
- Input sanitization and validation

## 📈 Performance & Scaling

### Current Capabilities

- Process 1,000+ images per job
- Real-time progress tracking
- Background processing (non-blocking)
- Concurrent file processing

### Future Scaling

- Horizontal scaling with multiple instances
- Queue-based job management (Redis/Celery)
- Cloud-native auto-scaling
- Load balancing support

## 🚨 Current Limitations

- **Palm Model**: Currently simulated (ready for real model integration)
- **Storage**: Local file system (easily upgradeable to cloud)
- **Database**: SQLite (can upgrade to PostgreSQL)
- **Authentication**: Basic (ready for production auth)

## 🤝 Contributing

This is a capstone project demonstrating MLOps best practices. The code is well-commented and designed for educational purposes.

## 📝 License

Educational project - ensure proper licensing for commercial use of the Palm model or other components.

## 🆘 Support

For issues or questions:

1. Check the [instructions.md](instructions.md) file
2. Review the API documentation at `/docs`
3. Check the logs for error messages
4. Verify all prerequisites are installed

## 🎉 Success Metrics

When running successfully, you should see:

- ✅ API server starts without errors
- ✅ Database initializes properly
- ✅ File uploads are accepted
- ✅ Processing jobs are created
- ✅ COCO results are generated
- ✅ Webhook notifications are sent
- ✅ Progress tracking works in real-time

---

**Ready to process your geospatial data? Start with `docker-compose up --build` and visit `http://localhost:8000/docs` to explore the API!** 🚀

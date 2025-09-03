@echo off
echo 🚀 Setting up Environment Variables for MLOps Pipeline with GCP
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

REM Check if .env file exists
if exist .env (
    echo ⚠️ .env file already exists!
    set /p overwrite="Do you want to overwrite it? (y/N): "
    if /i not "%overwrite%"=="y" (
        echo ❌ Setup cancelled. .env file unchanged.
        pause
        exit /b 0
    )
)

echo 📝 Creating .env file...

REM Create .env file with GCP configuration
(
echo # GCP Configuration
echo GOOGLE_APPLICATION_CREDENTIALS=./key.json
echo GCP_BUCKET_NAME=aya-internship-mlops-bucket
echo GCP_BUCKET_REGION=us-central1
echo ENABLE_GCP_UPLOAD=true
echo.
echo # API Configuration
echo API_BASE=http://localhost:8000
echo.
echo # Optional: Webhook Configuration
echo WEBHOOK_URL=https://requestcatcher.com/test
echo.
echo # Optional: Database Configuration
echo DATABASE_URL=sqlite:///mlops_pipeline.db
echo.
echo # Optional: Logging Configuration
echo LOG_LEVEL=INFO
) > .env

if exist .env (
    echo ✅ .env file created successfully!
    echo.
    echo 🎉 Environment setup completed!
    echo.
    echo 📋 Next steps:
    echo    1. Make sure you have GCP credentials in key.json
    echo    2. Start the MLOps pipeline: docker-compose up
    echo    3. Test GCP uploads: python test_gcp_uploads.py
    echo    4. Or test with local script: python test_real_files.py
    echo.
    echo 💡 Your files will now be automatically uploaded to Google Cloud Storage!
    echo 🌐 Access them at: https://console.cloud.google.com/storage/browser/aya-internship-mlops-bucket
) else (
    echo ❌ Failed to create .env file
)

echo.
pause

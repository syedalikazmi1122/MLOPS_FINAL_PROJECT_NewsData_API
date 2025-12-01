# 🚀 Phase III: CI/CD & Model Serving - Getting Started

## ✅ What We Just Created

1. **FastAPI Model Serving API** (`api/app.py`)
   - Prediction endpoint: `/predict`
   - Health check: `/health`
   - Model listing: `/models`
   - Model version info: `/models/{model_name}/versions`

2. **Dockerfile for API** (`Dockerfile.api`)
   - Python 3.11 slim base image
   - All dependencies installed
   - Health check configured
   - Exposes port 8000

3. **API Requirements** (`api/requirements.txt`)
   - FastAPI, Uvicorn, Pydantic
   - MLflow for model loading
   - Data processing libraries

## 🎯 Next Steps

### Step 1: Test API Locally (15 minutes)

```powershell
# Install API dependencies
pip install -r api/requirements.txt

# Set MLflow environment variables (for Dagshub)
$env:MLFLOW_TRACKING_URI = "https://dagshub.com/i222472/my-first-repo.mlflow"
$env:MLFLOW_TRACKING_USERNAME = "i222472"
$env:MLFLOW_TRACKING_PASSWORD = "YOUR_TOKEN"

# Run API
cd api
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Or from project root:
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

**Test endpoints:**
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Models: http://localhost:8000/models

### Step 2: Test Docker Build (10 minutes)

```powershell
# Build Docker image
docker build -f Dockerfile.api -t earthquake-api:latest .

# Run container
docker run -d \
  --name earthquake-api \
  -p 8000:8000 \
  -e MLFLOW_TRACKING_URI="https://dagshub.com/i222472/my-first-repo.mlflow" \
  -e MLFLOW_TRACKING_USERNAME="i222472" \
  -e MLFLOW_TRACKING_PASSWORD="YOUR_TOKEN" \
  earthquake-api:latest

# Check logs
docker logs earthquake-api

# Test health
curl http://localhost:8000/health
```

### Step 3: Add to docker-compose.yml (10 minutes)

We'll add the API service to docker-compose.yml so it runs alongside Airflow and MinIO.

### Step 4: Create GitHub Repository Structure (30 minutes)

- Create dev, test, master branches
- Set up branch protection rules
- Configure PR requirements

### Step 5: Create GitHub Actions Workflows (2-3 hours)

- Feature → dev: Linting + tests
- dev → test: Model retraining + CML
- test → master: Docker build + push to Docker Hub

## 📋 API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-30T12:00:00",
  "model_loaded": true,
  "model_info": {
    "model_name": "earthquake_magnitude_predictor",
    "version": "1",
    "stage": "Production"
  }
}
```

### `POST /predict`
Make predictions.

**Request:**
```json
{
  "features": [
    {
      "latitude": 34.0522,
      "longitude": -118.2437,
      "depth": 10.5,
      "mag_lag1": 3.5,
      "mag_lag2": 3.2,
      "mag_rolling_mean_7": 3.4
    }
  ],
  "model_name": "earthquake_magnitude_predictor",
  "stage": "Production"
}
```

**Response:**
```json
{
  "predictions": [3.7],
  "model_info": {
    "model_name": "earthquake_magnitude_predictor",
    "version": "1",
    "stage": "Production"
  },
  "inference_time_ms": 12.5
}
```

### `GET /models`
List all models in registry.

### `GET /models/{model_name}/versions`
List versions of a specific model.

## 🔍 Testing the API

### Using curl:

```powershell
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/models

# Make prediction (example)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [{
      "latitude": 34.0522,
      "longitude": -118.2437,
      "depth": 10.5
    }]
  }'
```

### Using Python:

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Make prediction
prediction_request = {
    "features": [{
        "latitude": 34.0522,
        "longitude": -118.2437,
        "depth": 10.5,
        "mag_lag1": 3.5
    }]
}
response = requests.post("http://localhost:8000/predict", json=prediction_request)
print(response.json())
```

## ⚠️ Important Notes

1. **Model Must Be in Registry**: The API loads models from MLflow Model Registry. Make sure you've trained and registered a model first.

2. **Dagshub Authentication**: Set `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` environment variables.

3. **Feature Names**: The API expects feature names that match what the model was trained on. Check your training script for exact feature names.

4. **Model Stage**: By default, the API loads from "Production" stage. You can specify "Staging" or `null` for latest version.

## 🎯 Current Status

- ✅ FastAPI service created
- ✅ Dockerfile created
- ✅ Requirements file created
- ⏳ Next: Test locally, then add to docker-compose.yml

---

**Ready to test! Start with Step 1 above.** 🚀


#!/usr/bin/env python3
"""
FastAPI Model Serving API for Earthquake Prediction.

This API:
- Loads models from MLflow Model Registry
- Provides prediction endpoints
- Includes health check and metrics endpoints
- Handles Dagshub authentication

Usage:
    uvicorn api.app:app --host 0.0.0.0 --port 8000
"""

import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Earthquake Prediction API",
    description="MLOps Model Serving API for Earthquake Magnitude Prediction",
    version="1.0.0"
)

# Global variables for model management
model_cache: Dict[str, any] = {}
model_metadata: Dict[str, dict] = {}
mlflow_client: Optional[MlflowClient] = None

# Prometheus metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

INFERENCE_LATENCY = Histogram(
    'api_inference_latency_ms',
    'API inference latency in milliseconds',
    buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000]
)

DATA_DRIFT_RATIO = Gauge(
    'api_data_drift_ratio',
    'Ratio of requests with out-of-distribution features (data drift proxy)',
)

ACTIVE_REQUESTS = Gauge(
    'api_active_requests',
    'Number of active requests being processed'
)


def setup_mlflow():
    """Configure MLflow tracking URI and authentication."""
    global mlflow_client
    
    mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    if not mlflow_tracking_uri:
        logger.warning("MLFLOW_TRACKING_URI not set, using local tracking")
        mlflow_tracking_uri = "file:./mlruns"
    
    # Handle Dagshub authentication
    mlflow_username = os.getenv('MLFLOW_TRACKING_USERNAME')
    mlflow_password = os.getenv('MLFLOW_TRACKING_PASSWORD')
    
    if mlflow_username and mlflow_password:
        import urllib.parse
        parsed = urllib.parse.urlparse(mlflow_tracking_uri)
        auth_uri = f"{parsed.scheme}://{mlflow_username}:{mlflow_password}@{parsed.netloc}{parsed.path}"
        mlflow.set_tracking_uri(auth_uri)
        logger.info(f"MLflow tracking URI configured (authenticated): {parsed.scheme}://{parsed.netloc}{parsed.path}")
    else:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        logger.info(f"MLflow tracking URI configured: {mlflow_tracking_uri}")
    
    mlflow_client = MlflowClient()
    logger.info("MLflow client initialized")


def load_model_from_registry(model_name: str, stage: str = "Production") -> tuple:
    """
    Load model from MLflow Model Registry.
    
    Args:
        model_name: Name of the registered model
        stage: Model stage (Production, Staging, None)
    
    Returns:
        (model, model_version) tuple
    """
    try:
        # Get latest model version from registry
        if stage:
            model_version = mlflow_client.get_latest_versions(
                model_name,
                stages=[stage]
            )
        else:
            model_version = mlflow_client.get_latest_versions(model_name)
        
        if not model_version:
            raise ValueError(f"No model found for {model_name} in stage {stage}")
        
        latest_version = model_version[0]
        model_uri = f"models:/{model_name}/{stage}" if stage else f"models:/{model_name}/{latest_version.version}"
        
        logger.info(f"Loading model: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)
        
        return model, latest_version
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {str(e)}")
        raise


def load_model(model_name: str = "earthquake_magnitude_predictor", stage: str = "Production"):
    """Load and cache model."""
    cache_key = f"{model_name}_{stage}"
    
    if cache_key in model_cache:
        logger.info(f"Using cached model: {cache_key}")
        return model_cache[cache_key], model_metadata[cache_key]
    
    logger.info(f"Loading model: {model_name} (stage: {stage})")
    model, version_info = load_model_from_registry(model_name, stage)
    
    # Cache model
    model_cache[cache_key] = model
    model_metadata[cache_key] = {
        "model_name": model_name,
        "version": version_info.version,
        "stage": stage,
        "run_id": version_info.run_id,
        "loaded_at": datetime.now().isoformat()
    }
    
    logger.info(f"Model loaded successfully: {model_name} v{version_info.version}")
    return model, model_metadata[cache_key]


# Initialize MLflow on startup
@app.on_event("startup")
async def startup_event():
    """Initialize MLflow and load default model on startup."""
    logger.info("Starting Earthquake Prediction API...")
    setup_mlflow()
    
    # Try to load default model (may fail if no model in registry yet)
    try:
        load_model("earthquake_magnitude_predictor", "Production")
        logger.info("Default model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load default model: {str(e)}")
        logger.info("API will start, but predictions will fail until model is available")


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for predictions."""
    features: List[Dict[str, float]] = Field(
        ...,
        description="List of feature dictionaries for prediction",
        example=[
            {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "depth": 10.5,
                "mag_lag1": 3.5,
                "mag_lag2": 3.2,
                "mag_rolling_mean_7": 3.4,
                # ... other features
            }
        ]
    )
    model_name: Optional[str] = Field(
        default="earthquake_magnitude_predictor",
        description="Name of the model to use"
    )
    stage: Optional[str] = Field(
        default="Production",
        description="Model stage (Production, Staging, None)"
    )


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    predictions: List[float] = Field(..., description="Predicted magnitudes")
    model_info: Dict = Field(..., description="Model metadata")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    model_loaded: bool
    model_info: Optional[Dict] = None


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Earthquake Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
    
    model_loaded = False
    model_info = None
    
    try:
        _, info = load_model()
        model_loaded = True
        model_info = info
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        timestamp=datetime.now().isoformat(),
        model_loaded=model_loaded,
        model_info=model_info
    )


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """
    Predict earthquake magnitudes.
    
    Args:
        request: Prediction request with features
    
    Returns:
        Predictions and model metadata
    """
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    try:
        # Load model
        model, model_info = load_model(request.model_name, request.stage)
        
        # Convert features to DataFrame
        features_df = pd.DataFrame(request.features)
        
        # Validate features
        if features_df.empty:
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='400').inc()
            ACTIVE_REQUESTS.dec()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No features provided"
            )
        
        # Check for data drift (out-of-distribution features)
        # Simple heuristic: check if any feature values are outside reasonable ranges
        drift_detected = False
        if not features_df.empty:
            # Example: check if magnitude-related features are in reasonable range (0-10)
            magnitude_cols = [col for col in features_df.columns if 'mag' in col.lower()]
            if magnitude_cols:
                for col in magnitude_cols:
                    if (features_df[col] < 0).any() or (features_df[col] > 10).any():
                        drift_detected = True
                        break
            
            # Check latitude/longitude ranges
            if 'latitude' in features_df.columns:
                if (features_df['latitude'] < -90).any() or (features_df['latitude'] > 90).any():
                    drift_detected = True
            if 'longitude' in features_df.columns:
                if (features_df['longitude'] < -180).any() or (features_df['longitude'] > 180).any():
                    drift_detected = True
        
        # Update data drift ratio (simple: 1 if drift detected, 0 otherwise)
        # In production, this would be more sophisticated
        DATA_DRIFT_RATIO.set(1.0 if drift_detected else 0.0)
        
        # Scale features if model has scaler
        if hasattr(model, 'scaler'):
            features_scaled = model.scaler.transform(features_df)
        else:
            features_scaled = features_df.values
        
        # Make predictions
        predictions = model.predict(features_scaled)
        predictions_list = predictions.tolist() if isinstance(predictions, np.ndarray) else list(predictions)
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Record metrics
        INFERENCE_LATENCY.observe(inference_time)
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()
        ACTIVE_REQUESTS.dec()
        
        logger.info(f"Made {len(predictions_list)} predictions in {inference_time:.2f}ms")
        
        return PredictionResponse(
            predictions=predictions_list,
            model_info=model_info,
            inference_time_ms=inference_time
        )
    
    except ValueError as e:
        logger.error(f"Value error in prediction: {str(e)}")
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='400').inc()
        ACTIVE_REQUESTS.dec()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='500').inc()
        ACTIVE_REQUESTS.dec()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/models", tags=["Models"])
async def list_models():
    """List available models in MLflow registry."""
    try:
        if not mlflow_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MLflow client not initialized"
            )
        
        models = mlflow_client.search_registered_models()
        model_list = []
        
        for model in models:
            for version in model.latest_versions:
                model_list.append({
                    "name": model.name,
                    "version": version.version,
                    "stage": version.current_stage,
                    "run_id": version.run_id,
                    "created_at": version.creation_timestamp
                })
        
        return {"models": model_list}
    
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@app.get("/models/{model_name}/versions", tags=["Models"])
async def list_model_versions(model_name: str):
    """List versions of a specific model."""
    try:
        if not mlflow_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MLflow client not initialized"
            )
        
        versions = mlflow_client.search_model_versions(f"name='{model_name}'")
        version_list = []
        
        for version in versions:
            version_list.append({
                "version": version.version,
                "stage": version.current_stage,
                "run_id": version.run_id,
                "created_at": version.creation_timestamp,
                "status": version.status
            })
        
        return {"model_name": model_name, "versions": version_list}
    
    except Exception as e:
        logger.error(f"Error listing model versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list model versions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


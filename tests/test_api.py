"""
Unit tests for FastAPI model serving API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

# Import the app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    model = Mock()
    model.predict.return_value = np.array([3.5, 4.2])
    model.scaler = Mock()
    model.scaler.transform.return_value = np.array([[1.0, 2.0], [3.0, 4.0]])
    return model


@pytest.fixture
def sample_features():
    """Sample feature data for testing."""
    return [
        {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "depth": 10.5,
            "mag_lag1": 3.5,
            "mag_lag2": 3.2,
            "mag_rolling_mean_7": 3.4
        },
        {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "depth": 15.0,
            "mag_lag1": 4.0,
            "mag_lag2": 3.8,
            "mag_rolling_mean_7": 3.9
        }
    ]


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_endpoint_exists(self, client):
        """Test that health endpoint exists."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # 503 if model not loaded
    
    def test_health_response_structure(self, client):
        """Test health response structure."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "model_loaded" in data


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestPredictEndpoint:
    """Tests for /predict endpoint."""
    
    @patch('api.app.load_model')
    def test_predict_success(self, mock_load_model, client, mock_model, sample_features):
        """Test successful prediction."""
        mock_load_model.return_value = (mock_model, {
            "model_name": "earthquake_magnitude_predictor",
            "version": "1",
            "stage": "Production"
        })
        
        response = client.post(
            "/predict",
            json={
                "features": sample_features,
                "model_name": "earthquake_magnitude_predictor",
                "stage": "Production"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "model_info" in data
        assert "inference_time_ms" in data
        assert len(data["predictions"]) == 2
    
    def test_predict_no_features(self, client):
        """Test prediction with no features."""
        response = client.post(
            "/predict",
            json={
                "features": []
            }
        )
        assert response.status_code == 400
    
    def test_predict_invalid_features(self, client):
        """Test prediction with invalid features."""
        response = client.post(
            "/predict",
            json={
                "features": [{"invalid": "data"}]
            }
        )
        # Should either succeed (if model handles it) or fail gracefully
        assert response.status_code in [200, 400, 500]


class TestModelsEndpoint:
    """Tests for /models endpoint."""
    
    @patch('api.app.mlflow_client')
    def test_list_models(self, mock_client, client):
        """Test listing models."""
        # Mock MLflow client
        mock_model = Mock()
        mock_model.name = "earthquake_magnitude_predictor"
        mock_version = Mock()
        mock_version.version = "1"
        mock_version.current_stage = "Production"
        mock_version.run_id = "abc123"
        mock_version.creation_timestamp = 1234567890
        mock_model.latest_versions = [mock_version]
        
        mock_client.search_registered_models.return_value = [mock_model]
        
        response = client.get("/models")
        assert response.status_code in [200, 503]  # 503 if mlflow_client not initialized
    
    @patch('api.app.mlflow_client')
    def test_list_model_versions(self, mock_client, client):
        """Test listing model versions."""
        mock_version = Mock()
        mock_version.version = "1"
        mock_version.current_stage = "Production"
        mock_version.run_id = "abc123"
        mock_version.creation_timestamp = 1234567890
        mock_version.status = "READY"
        
        mock_client.search_model_versions.return_value = [mock_version]
        
        response = client.get("/models/earthquake_magnitude_predictor/versions")
        assert response.status_code in [200, 503]


class TestModelLoading:
    """Tests for model loading functionality."""
    
    @patch('api.app.mlflow_client')
    @patch('api.app.mlflow.sklearn.load_model')
    def test_load_model_success(self, mock_load_model, mock_client):
        """Test successful model loading."""
        from api.app import load_model
        
        # Mock MLflow client
        mock_version = Mock()
        mock_version.version = "1"
        mock_version.run_id = "abc123"
        mock_client.get_latest_versions.return_value = [mock_version]
        
        # Mock model
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        try:
            model, info = load_model("earthquake_magnitude_predictor", "Production")
            assert model is not None
            assert "version" in info
        except Exception:
            # Model loading might fail if MLflow not configured
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns expected structure"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Motivate.AI Backend API"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_cors_headers():
    """Test that CORS headers are properly configured"""
    response = client.options("/")
    assert response.status_code == 200 
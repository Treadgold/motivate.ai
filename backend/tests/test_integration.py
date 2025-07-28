"""
Integration tests that require database setup
These tests use the test database fixtures from conftest.py
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_create_project_with_db(test_client):
    """Test project creation with database"""
    project_data = {
        "title": "Integration Test Project",
        "description": "A test project for integration testing",
        "priority": "high"
    }
    
    response = test_client.post("/api/v1/projects", json=project_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == project_data["title"]
    assert data["description"] == project_data["description"]
    assert data["priority"] == project_data["priority"]
    assert "id" in data

def test_get_projects_with_db(test_client):
    """Test getting all projects"""
    # First create a project
    project_data = {"title": "Test Project for List"}
    test_client.post("/api/v1/projects", json=project_data)
    
    # Then get all projects
    response = test_client.get("/api/v1/projects")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_health_endpoint_with_client(test_client):
    """Test health endpoint using test client"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint_with_client(test_client):
    """Test root endpoint using test client"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Motivate.AI Backend API" 
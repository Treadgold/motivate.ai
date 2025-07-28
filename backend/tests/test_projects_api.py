import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app

client = TestClient(app)

class TestProjectsAPI:
    """Test suite for projects API endpoints"""
    
    def test_create_project_success(self):
        """Test successful project creation"""
        project_data = {
            "title": "Test Project",
            "description": "A test project for validation",
            "priority": "high",
            "location": "home office"
        }
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == project_data["title"]
        assert data["description"] == project_data["description"]
        assert data["priority"] == project_data["priority"]
        assert data["location"] == project_data["location"]
        assert "id" in data
        assert "created_at" in data
        
    def test_create_project_minimal_data(self):
        """Test project creation with minimal required data"""
        project_data = {"title": "Minimal Project"}
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == project_data["title"]
        assert data["priority"] == "medium"  # Default value
        
    def test_create_project_empty_title(self):
        """Test project creation fails with empty title"""
        project_data = {"title": ""}
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 422  # Validation error
        
    def test_get_all_projects(self):
        """Test retrieving all projects"""
        # Create a test project first
        project_data = {"title": "Test List Project"}
        client.post("/api/v1/projects", json=project_data)
        
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
    def test_get_project_by_id(self):
        """Test retrieving a specific project by ID"""
        # Create a test project first
        project_data = {"title": "Test Get Project"}
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["title"] == project_data["title"]
        
    def test_get_nonexistent_project(self):
        """Test retrieving a project that doesn't exist"""
        response = client.get("/api/v1/projects/99999")
        assert response.status_code == 404
        
    def test_update_project(self):
        """Test updating an existing project"""
        # Create a test project first
        project_data = {"title": "Original Title"}
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Update the project
        update_data = {"title": "Updated Title", "priority": "high"}
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["priority"] == update_data["priority"]
        
    def test_delete_project(self):
        """Test deleting a project"""
        # Create a test project first
        project_data = {"title": "To Be Deleted"}
        create_response = client.post("/api/v1/projects", json=project_data)
        project_id = create_response.json()["id"]
        
        # Delete the project
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404 
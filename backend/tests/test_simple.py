"""
Simple standalone tests for basic functionality validation
These tests don't require database setup and run quickly
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_basic_imports():
    """Test that all core modules can be imported"""
    try:
        import main
        import database
        from services import ai_service
        from api import projects, tasks, suggestions, activity
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")

def test_fastapi_app_creation():
    """Test that FastAPI app can be created"""
    from main import app
    assert app is not None
    assert hasattr(app, 'routes')

def test_ai_service_initialization():
    """Test AI service can be initialized"""
    from services.ai_service import AIService
    ai_service = AIService()
    assert ai_service.base_url is not None
    assert ai_service.model is not None
    assert ai_service.timeout > 0

def test_basic_health_endpoint():
    """Test the health endpoint with running API"""
    import httpx
    
    try:
        # Test the actual running API
        with httpx.Client() as client:
            response = client.get("http://localhost:8010/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    except httpx.ConnectError:
        # If API not running, skip this test
        import pytest
        pytest.skip("API not running at localhost:8010")

def test_root_endpoint():
    """Test the root endpoint with running API"""
    import httpx
    
    try:
        # Test the actual running API
        with httpx.Client() as client:
            response = client.get("http://localhost:8010/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data
    except httpx.ConnectError:
        # If API not running, skip this test
        import pytest
        pytest.skip("API not running at localhost:8010") 
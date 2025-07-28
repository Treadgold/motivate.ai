"""
Alternative simple endpoint tests that bypass TestClient version issues
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_endpoints_exist():
    """Test that endpoints are properly registered"""
    from main import app
    
    # Check that routes are registered
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/health" in routes
    
def test_app_configuration():
    """Test FastAPI app configuration"""
    from main import app
    
    assert app.title == "Motivate.AI API"
    assert app.description == "AI-guided project companion backend"
    assert app.version == "1.0.0"

def test_middleware_configured():
    """Test that CORS middleware is configured"""
    from main import app
    
    # Check that middleware is added (look at middleware stack)
    middleware_found = False
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and 'CORS' in str(middleware.cls):
            middleware_found = True
            break
    assert middleware_found

def test_routers_included():
    """Test that API routers are properly included"""
    from main import app
    
    # Check that API routes are registered
    api_routes = [route.path for route in app.routes if route.path.startswith("/api")]
    assert len(api_routes) > 0 
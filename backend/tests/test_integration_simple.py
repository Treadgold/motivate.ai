"""
Simple integration tests that test database functionality without TestClient
These tests focus on testing the business logic with database operations
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_database_tables_creation():
    """Test that database tables can be created"""
    try:
        from database import engine, Base
        # This should work without errors
        Base.metadata.create_all(bind=engine)
        assert True
    except Exception as e:
        pytest.fail(f"Database table creation failed: {e}")

def test_project_model_database_operations():
    """Test basic project model database operations"""
    try:
        from database import SessionLocal
        from models.project import Project
        
        # Create a session
        db = SessionLocal()
        
        # Create a test project
        test_project = Project(
            title="Integration Test Project",
            description="Testing database operations",
            status="active",
            priority="medium"
        )
        
        # Add to database
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        
        # Verify it was saved
        assert test_project.id is not None
        assert test_project.title == "Integration Test Project"
        
        # Query it back
        retrieved_project = db.query(Project).filter(Project.id == test_project.id).first()
        assert retrieved_project is not None
        assert retrieved_project.title == "Integration Test Project"
        
        # Clean up
        db.delete(test_project)
        db.commit()
        db.close()
        
    except Exception as e:
        pytest.fail(f"Database operations failed: {e}")

def test_api_routes_registration():
    """Test that API routes are properly registered"""
    try:
        from main import app
        from api import projects, tasks, activity, suggestions
        
        # Check that routes exist in the app
        route_paths = [route.path for route in app.routes]
        
        # Should have basic routes
        assert "/" in route_paths
        assert "/health" in route_paths
        
        # Should have API routes (may vary based on router configuration)
        api_routes = [path for path in route_paths if path.startswith("/api")]
        assert len(api_routes) > 0, "No API routes found"
        
    except Exception as e:
        pytest.fail(f"Route registration test failed: {e}")

def test_dependency_imports():
    """Test that all required dependencies can be imported"""
    try:
        # Test core imports
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        
        # Test project-specific imports
        from main import app
        from database import engine, SessionLocal, Base
        from models.project import Project
        from models.task import Task
        from models.activity import Activity
        
        assert app is not None
        assert engine is not None
        assert SessionLocal is not None
        assert Base is not None
        
    except ImportError as e:
        pytest.fail(f"Required dependency import failed: {e}") 
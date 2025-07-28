"""
Simple database tests to verify models and basic database functionality
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_database_models_import():
    """Test that database models can be imported"""
    try:
        from models.project import Project
        from models.task import Task 
        from models.activity import Activity
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import database models: {e}")

def test_database_connection():
    """Test basic database connection"""
    try:
        from database import get_db, engine
        # Just test that we can create an engine and get_db function exists
        assert engine is not None
        assert callable(get_db)
    except Exception as e:
        pytest.fail(f"Database connection test failed: {e}")

def test_project_model_structure():
    """Test that Project model has expected fields"""
    from models.project import Project
    
    # Check that the model has expected attributes
    expected_fields = ['id', 'title', 'description', 'status', 'priority', 'created_at']
    
    for field in expected_fields:
        assert hasattr(Project, field), f"Project model missing field: {field}"

def test_basic_project_creation():
    """Test basic project object creation (not database insertion)"""
    from models.project import Project
    
    # Create a project object (not saving to database)
    project = Project(
        title="Test Project",
        description="Test Description",
        status="active",
        priority="medium"
    )
    
    assert project.title == "Test Project"
    assert project.description == "Test Description"
    assert project.status == "active"
    assert project.priority == "medium" 
"""
Tests for AI-powered task management features

Tests the enhanced task API with CRUD operations, bulk creation,
AI tools service, and task splitting functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from services.ai_tools import AITaskTools, get_ai_tools
from services.ai_service import AIService
from models.task import Task
from models.project import Project


def test_get_single_task(test_client):
    """Test getting a single task by ID"""
    # First create a project
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Test Project",
        "description": "Test project for task testing"
    })
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]
    
    # Create a task
    task_response = test_client.post("/api/v1/tasks", json={
        "project_id": project_id,
        "title": "Test Task",
        "description": "A test task",
        "estimated_minutes": 30,
        "priority": "high",
        "energy_level": "medium"
    })
    assert task_response.status_code == 200
    task_id = task_response.json()["id"]
    
    # Get the task
    get_response = test_client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200
    
    task_data = get_response.json()
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "A test task"
    assert task_data["estimated_minutes"] == 30
    assert task_data["priority"] == "high"
    assert task_data["energy_level"] == "medium"


def test_update_task(test_client):
    """Test updating a task"""
    # Create project and task
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Update Test Project"
    })
    project_id = project_response.json()["id"]
    
    task_response = test_client.post("/api/v1/tasks", json={
        "project_id": project_id,
        "title": "Original Task",
        "estimated_minutes": 15
    })
    task_id = task_response.json()["id"]
    
    # Update the task
    update_response = test_client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "Updated Task",
        "description": "Updated description",
        "estimated_minutes": 25,
        "priority": "low"
    })
    assert update_response.status_code == 200
    
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Updated description"
    assert updated_task["estimated_minutes"] == 25
    assert updated_task["priority"] == "low"


def test_delete_task(test_client):
    """Test deleting a task"""
    # Create project and task
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Delete Test Project"
    })
    project_id = project_response.json()["id"]
    
    task_response = test_client.post("/api/v1/tasks", json={
        "project_id": project_id,
        "title": "Task to Delete"
    })
    task_id = task_response.json()["id"]
    
    # Delete the task
    delete_response = test_client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]
    
    # Verify task is gone
    get_response = test_client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_bulk_task_creation(test_client):
    """Test creating multiple tasks at once"""
    # Create project
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Bulk Test Project"
    })
    project_id = project_response.json()["id"]
    
    # Create multiple tasks
    bulk_response = test_client.post("/api/v1/tasks/bulk", json={
        "tasks": [
            {
                "project_id": project_id,
                "title": "Bulk Task 1",
                "description": "First bulk task",
                "estimated_minutes": 10
            },
            {
                "project_id": project_id,
                "title": "Bulk Task 2", 
                "description": "Second bulk task",
                "estimated_minutes": 15,
                "priority": "high"
            },
            {
                "project_id": project_id,
                "title": "Bulk Task 3",
                "estimated_minutes": 20,
                "energy_level": "high"
            }
        ]
    })
    
    assert bulk_response.status_code == 200
    created_tasks = bulk_response.json()
    assert len(created_tasks) == 3
    assert created_tasks[0]["title"] == "Bulk Task 1"
    assert created_tasks[1]["priority"] == "high"
    assert created_tasks[2]["energy_level"] == "high"


def test_ai_tools_get_task_details(test_db):
    """Test AI tools can retrieve task details"""
    db = test_db()
    
    # Create project and task directly in database
    project = Project(title="AI Tools Test Project", description="Test project")
    db.add(project)
    db.commit()
    db.refresh(project)
    
    task = Task(
        project_id=project.id,
        title="AI Test Task",
        description="Task for AI tools testing",
        priority="medium",
        estimated_minutes=25,
        energy_level="high",
        context="when focused"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Test AI tools
    ai_tools = AITaskTools(db)
    task_details = ai_tools.get_task_details(task.id)
    
    assert task_details is not None
    assert task_details["title"] == "AI Test Task"
    assert task_details["description"] == "Task for AI tools testing"
    assert task_details["priority"] == "medium"
    assert task_details["estimated_minutes"] == 25
    assert task_details["energy_level"] == "high"
    assert task_details["context"] == "when focused"
    assert task_details["project"]["title"] == "AI Tools Test Project"


def test_ai_tools_create_multiple_tasks(test_db):
    """Test AI tools can create multiple tasks"""
    db = test_db()
    
    # Create project
    project = Project(title="Multi-Task Project")
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Test creating multiple tasks via AI tools
    ai_tools = AITaskTools(db)
    tasks_data = [
        {
            "project_id": project.id,
            "title": "AI Created Task 1",
            "description": "First AI-created task",
            "estimated_minutes": 15
        },
        {
            "project_id": project.id,
            "title": "AI Created Task 2",
            "description": "Second AI-created task",
            "priority": "high",
            "energy_level": "low"
        }
    ]
    
    created_tasks = ai_tools.create_multiple_tasks(tasks_data)
    
    assert len(created_tasks) == 2
    assert created_tasks[0]["title"] == "AI Created Task 1"
    assert created_tasks[1]["priority"] == "high"
    assert created_tasks[1]["energy_level"] == "low"


@patch('services.ai_service.httpx.AsyncClient')
def test_task_split_with_mocked_ai(mock_client, test_client):
    """Test task splitting with mocked AI response"""
    # Create project and task
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Split Test Project",
        "description": "Project for testing task splitting"
    })
    project_id = project_response.json()["id"]
    
    task_response = test_client.post("/api/v1/tasks", json={
        "project_id": project_id,
        "title": "Complex Task to Split",
        "description": "This is a complex task that should be split into smaller pieces",
        "estimated_minutes": 60,
        "priority": "high"
    })
    task_id = task_response.json()["id"]
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '''[
            {
                "title": "Plan the complex task approach",
                "description": "Spend time planning how to tackle the complex task",
                "estimated_minutes": 15,
                "energy_level": "medium",
                "context": "when you need to get started",
                "reasoning": "Planning reduces overwhelm"
            },
            {
                "title": "Execute first phase of task",
                "description": "Begin working on the first part of the complex task",
                "estimated_minutes": 20,
                "energy_level": "high",
                "context": "when you have focus",
                "reasoning": "Breaking into phases makes it manageable"
            },
            {
                "title": "Complete and review task",
                "description": "Finish the task and review the results",
                "estimated_minutes": 25,
                "energy_level": "medium",
                "context": "anytime",
                "reasoning": "Proper completion ensures quality"
            }
        ]'''
    }
    
    # Configure mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    # Test task splitting
    split_response = test_client.post(f"/api/v1/tasks/{task_id}/split")
    assert split_response.status_code == 200
    
    split_data = split_response.json()
    assert "original_task" in split_data
    assert "suggested_tasks" in split_data
    assert split_data["original_task"]["title"] == "Complex Task to Split"
    assert len(split_data["suggested_tasks"]) == 3
    assert split_data["suggested_tasks"][0]["title"] == "Plan the complex task approach"


def test_task_split_fallback(test_client):
    """Test task splitting falls back gracefully when AI is unavailable"""
    # Create project and task
    project_response = test_client.post("/api/v1/projects", json={
        "title": "Fallback Test Project"
    })
    project_id = project_response.json()["id"]
    
    task_response = test_client.post("/api/v1/tasks", json={
        "project_id": project_id,
        "title": "Task for Fallback Test",
        "estimated_minutes": 30
    })
    task_id = task_response.json()["id"]
    
    # Mock AI service to raise an exception (simulating AI unavailable)
    with patch('services.ai_service.httpx.AsyncClient') as mock_client:
        mock_client.side_effect = Exception("AI service unavailable")
        
        split_response = test_client.post(f"/api/v1/tasks/{task_id}/split")
        assert split_response.status_code == 200
        
        split_data = split_response.json()
        assert "suggested_tasks" in split_data
        assert len(split_data["suggested_tasks"]) == 3  # Fallback provides 3 tasks
        
        # Check that fallback tasks are reasonable
        suggested_tasks = split_data["suggested_tasks"]
        assert "Plan approach" in suggested_tasks[0]["title"]
        assert "Start work" in suggested_tasks[1]["title"]
        assert "Complete and review" in suggested_tasks[2]["title"]


def test_task_not_found_errors(test_client):
    """Test appropriate error handling for non-existent tasks"""
    # Test getting non-existent task
    get_response = test_client.get("/api/v1/tasks/99999")
    assert get_response.status_code == 404
    
    # Test updating non-existent task
    update_response = test_client.put("/api/v1/tasks/99999", json={"title": "Updated"})
    assert update_response.status_code == 404
    
    # Test deleting non-existent task
    delete_response = test_client.delete("/api/v1/tasks/99999")
    assert delete_response.status_code == 404
    
    # Test splitting non-existent task
    split_response = test_client.post("/api/v1/tasks/99999/split")
    assert split_response.status_code == 404 
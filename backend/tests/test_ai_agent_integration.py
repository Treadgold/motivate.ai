"""
Comprehensive Integration Tests for AI Agent

Tests the complete AI agent workflow including:
- Project and task setup
- AI agent preview generation
- Preview approval and execution
- Result verification
"""

import pytest
import sys
import json
import httpx
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app
from database import get_db, create_tables
from models.project import Project
from models.task import Task
from services.ai_agent_simple import AIAgent, OperationType, get_ai_agent


@pytest.fixture
def test_client():
    """Create test client with in-memory database"""
    # Use in-memory SQLite for testing
    import os
    os.environ["DATABASE_URL"] = "sqlite:///./test_ai_agent.db"
    
    # Create fresh tables
    create_tables()
    
    client = TestClient(app)
    yield client


@pytest.fixture
def sample_project_and_task(test_client):
    """Create a sample project and complex task for testing"""
    
    # Create a project
    project_data = {
        "title": "Website Redesign",
        "description": "Complete overhaul of company website",
        "location": "Remote"
    }
    
    project_response = test_client.post("/api/v1/projects", json=project_data)
    assert project_response.status_code == 200
    project = project_response.json()
    
    # Create a complex task that needs splitting
    task_data = {
        "project_id": project["id"],
        "title": "Implement user authentication system",
        "description": "Build complete user authentication with login, registration, password reset, email verification, and user profile management",
        "priority": "high",
        "estimated_minutes": 240,  # 4 hours - should be split
        "energy_level": "high",
        "context": "when you have deep focus time"
    }
    
    task_response = test_client.post("/api/v1/tasks", json=task_data)
    assert task_response.status_code == 200
    task = task_response.json()
    
    return project, task


def test_ai_agent_status(test_client):
    """Test that AI agent status endpoint works"""
    response = test_client.get("/api/v1/ai-agent/status")
    assert response.status_code == 200
    
    status = response.json()
    assert "status" in status
    assert "tools_available" in status
    assert status["tools_available"] > 0
    assert status["workflow_engine"] == "langgraph"


def test_ai_agent_supported_operations(test_client):
    """Test getting supported operations"""
    response = test_client.get("/api/v1/ai-agent/operations")
    assert response.status_code == 200
    
    operations = response.json()
    assert "supported_operations" in operations
    assert operations["total_operations"] == 5
    
    # Check that split_task operation exists
    split_task_op = next(
        (op for op in operations["supported_operations"] if op["name"] == "split_task"),
        None
    )
    assert split_task_op is not None
    assert "task_ids" in split_task_op["required_inputs"]


def test_ai_agent_preview_creation(test_client, sample_project_and_task):
    """Test creating an AI agent preview for task splitting"""
    project, task = sample_project_and_task
    
    # Request a preview for task splitting
    preview_request = {
        "operation": "split_task",
        "task_ids": [task["id"]],
        "context": {
            "user_preference": "prefer shorter tasks",
            "work_style": "focused sprints"
        }
    }
    
    # Mock the AI service to avoid needing actual Ollama
    with patch.object(AIAgent, '_analyze_task_splitting') as mock_analyze:
        # Mock AI response
        mock_analyze.return_value = {
            "analysis": {
                "ai_analysis": {
                    "reasoning_steps": [
                        "Task is too large at 240 minutes",
                        "Authentication system has clear sub-components",
                        "Can be broken into logical phases"
                    ],
                    "impact_assessment": "This split will make development more manageable and testable"
                },
                "impact_assessment": "This split will make development more manageable and testable",
                "recommendations": ["Test each component individually", "Focus on security best practices"]
            },
            "proposed_changes": [
                {
                    "action": "create_tasks",
                    "tasks": [
                        {
                            "title": "Design authentication database schema",
                            "description": "Create user tables, indexes, and relationships for authentication system",
                            "estimated_minutes": 45,
                            "priority": "high",
                            "energy_level": "medium",
                            "context": "when you need to think through data structure",
                            "project_id": project["id"]
                        },
                        {
                            "title": "Implement user registration API",
                            "description": "Build user registration endpoint with validation and email verification",
                            "estimated_minutes": 60,
                            "priority": "high",
                            "energy_level": "high",
                            "context": "when you have deep focus time",
                            "project_id": project["id"]
                        },
                        {
                            "title": "Implement login and session management",
                            "description": "Build login endpoint, JWT tokens, and session handling",
                            "estimated_minutes": 75,
                            "priority": "high",
                            "energy_level": "high",
                            "context": "when you have deep focus time",
                            "project_id": project["id"]
                        },
                        {
                            "title": "Add password reset functionality",
                            "description": "Implement password reset flow with secure token generation",
                            "estimated_minutes": 45,
                            "priority": "medium",
                            "energy_level": "medium",
                            "context": "when you have moderate focus",
                            "project_id": project["id"]
                        },
                        {
                            "title": "Build user profile management",
                            "description": "Create user profile update endpoints and validation",
                            "estimated_minutes": 30,
                            "priority": "medium",
                            "energy_level": "medium",
                            "context": "anytime",
                            "project_id": project["id"]
                        }
                    ],
                    "reasoning": "Split into logical development phases: schema design, core auth, secondary features"
                },
                {
                    "action": "delete_task",
                    "task_id": task["id"],
                    "reasoning": "Original task replaced by 5 focused subtasks"
                }
            ],
            "confidence_score": 0.9,
            "reasoning_steps": [
                "Task is too large at 240 minutes",
                "Authentication system has clear sub-components",
                "Can be broken into logical phases",
                "Each subtask is 30-75 minutes, ideal for focused work"
            ]
        }
        
        response = test_client.post("/api/v1/ai-agent/preview", json=preview_request)
        assert response.status_code == 200
        
        preview = response.json()
        assert preview["operation"] == "split_task"
        assert preview["confidence_score"] == 0.9
        assert len(preview["proposed_changes"]) == 2  # create_tasks + delete_task
        assert "preview_id" in preview
        
        # Verify the proposed subtasks
        create_action = next(
            change for change in preview["proposed_changes"] 
            if change["action"] == "create_tasks"
        )
        subtasks = create_action["tasks"]
        assert len(subtasks) == 5
        
        # Check that all subtasks are reasonably sized
        for subtask in subtasks:
            assert 30 <= subtask["estimated_minutes"] <= 75
            assert subtask["project_id"] == project["id"]
            assert subtask["title"] is not None
            assert subtask["description"] is not None
        
        return preview


def test_ai_agent_preview_details(test_client, sample_project_and_task):
    """Test getting preview details"""
    project, task = sample_project_and_task
    
    # First create a preview
    preview_request = {
        "operation": "split_task",
        "task_ids": [task["id"]]
    }
    
    with patch.object(AIAgent, '_analyze_task_splitting') as mock_analyze:
        mock_analyze.return_value = {
            "analysis": {"impact_assessment": "Test impact"},
            "proposed_changes": [{"action": "test", "reasoning": "test"}],
            "confidence_score": 0.8,
            "reasoning_steps": ["Test reasoning"]
        }
        
        preview_response = test_client.post("/api/v1/ai-agent/preview", json=preview_request)
        preview = preview_response.json()
        preview_id = preview["preview_id"]
        
        # Get preview details
        details_response = test_client.get(f"/api/v1/ai-agent/preview/{preview_id}")
        assert details_response.status_code == 200
        
        details = details_response.json()
        assert details["preview_id"] == preview_id
        assert details["operation"] == "split_task"
        assert details["status"] == "pending_approval"


def test_ai_agent_preview_cancellation(test_client, sample_project_and_task):
    """Test cancelling a preview"""
    project, task = sample_project_and_task
    
    # Create a preview
    preview_request = {
        "operation": "split_task",
        "task_ids": [task["id"]]
    }
    
    with patch.object(AIAgent, '_analyze_task_splitting') as mock_analyze:
        mock_analyze.return_value = {
            "analysis": {"impact_assessment": "Test"},
            "proposed_changes": [],
            "confidence_score": 0.8,
            "reasoning_steps": ["Test"]
        }
        
        preview_response = test_client.post("/api/v1/ai-agent/preview", json=preview_request)
        preview = preview_response.json()
        preview_id = preview["preview_id"]
        
        # Cancel the preview
        cancel_response = test_client.delete(f"/api/v1/ai-agent/preview/{preview_id}")
        assert cancel_response.status_code == 200
        
        # Verify it's deleted
        details_response = test_client.get(f"/api/v1/ai-agent/preview/{preview_id}")
        assert details_response.status_code == 404


def test_ai_agent_full_execution_workflow(test_client, sample_project_and_task):
    """Test the complete AI agent workflow from preview to execution"""
    project, task = sample_project_and_task
    
    # Step 1: Create preview
    preview_request = {
        "operation": "split_task",
        "task_ids": [task["id"]],
        "context": {"test": "full_workflow"}
    }
    
    subtasks_data = [
        {
            "title": "Plan authentication system",
            "description": "Design the overall authentication architecture",
            "estimated_minutes": 30,
            "priority": "high",
            "energy_level": "medium",
            "context": "when thinking through architecture",
            "project_id": project["id"]
        },
        {
            "title": "Implement user registration",
            "description": "Build user registration with validation",
            "estimated_minutes": 60,
            "priority": "high",
            "energy_level": "high",
            "context": "when you have focus time",
            "project_id": project["id"]
        }
    ]
    
    with patch.object(AIAgent, '_analyze_task_splitting') as mock_analyze:
        mock_analyze.return_value = {
            "analysis": {
                "impact_assessment": "Breaking down large task improves manageability",
                "recommendations": ["Focus on one component at a time"]
            },
            "proposed_changes": [
                {
                    "action": "create_tasks",
                    "tasks": subtasks_data,
                    "reasoning": "Split into manageable components"
                },
                {
                    "action": "delete_task",
                    "task_id": task["id"],
                    "reasoning": "Replace with subtasks"
                }
            ],
            "confidence_score": 0.85,
            "reasoning_steps": [
                "Original task is too large at 240 minutes",
                "Can be split into logical components",
                "Each subtask is appropriately sized"
            ]
        }
        
        preview_response = test_client.post("/api/v1/ai-agent/preview", json=preview_request)
        assert preview_response.status_code == 200
        preview = preview_response.json()
        preview_id = preview["preview_id"]
        
        # Step 2: Execute the preview
        # Mock the API calls that the agent would make
        with patch('httpx.post') as mock_post, \
             patch('httpx.delete') as mock_delete:
            
            # Mock successful task creation
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "message": "Tasks created successfully",
                    "tasks": [
                        {"id": 100, "title": "Plan authentication system"},
                        {"id": 101, "title": "Implement user registration"}
                    ]
                }
            )
            
            # Mock successful task deletion
            mock_delete.return_value = MagicMock(
                status_code=200,
                json=lambda: {"message": f"Task {task['id']} deleted successfully"}
            )
            
            execution_response = test_client.post(f"/api/v1/ai-agent/execute/{preview_id}")
            assert execution_response.status_code == 200
            
            execution_result = execution_response.json()
            assert execution_result["success"] is True
            assert execution_result["operation"] == "split_task"
            assert "executed_changes" in execution_result
            assert "execution_id" in execution_result
            
            # Verify the API calls were made
            assert mock_post.called
            assert mock_delete.called
            
            # Verify the preview is cleaned up
            details_response = test_client.get(f"/api/v1/ai-agent/preview/{preview_id}")
            assert details_response.status_code == 404


def test_ai_agent_error_handling(test_client, sample_project_and_task):
    """Test AI agent error handling scenarios"""
    project, task = sample_project_and_task
    
    # Test invalid operation
    invalid_request = {
        "operation": "invalid_operation",
        "task_ids": [task["id"]]
    }
    
    response = test_client.post("/api/v1/ai-agent/preview", json=invalid_request)
    assert response.status_code == 400
    assert "Unsupported operation" in response.json()["detail"]
    
    # Test missing task_ids for split_task
    missing_ids_request = {
        "operation": "split_task",
        "task_ids": []
    }
    
    response = test_client.post("/api/v1/ai-agent/preview", json=missing_ids_request)
    assert response.status_code == 400
    assert "task_ids are required" in response.json()["detail"]
    
    # Test executing non-existent preview
    fake_preview_id = "fake-preview-id-12345"
    response = test_client.post(f"/api/v1/ai-agent/execute/{fake_preview_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_ai_agent_fallback_analysis(test_client, sample_project_and_task):
    """Test AI agent fallback when AI service is unavailable"""
    project, task = sample_project_and_task
    
    preview_request = {
        "operation": "split_task",
        "task_ids": [task["id"]]
    }
    
    # Mock AI service failure to trigger fallback
    with patch.object(AIAgent, '_analyze_task_splitting') as mock_analyze:
        # Mock the method to call the fallback directly
        agent = get_ai_agent()
        mock_analyze.side_effect = lambda gathered_data, request: agent._fallback_task_analysis(
            gathered_data, request.get("task_ids", [])
        )
        
        response = test_client.post("/api/v1/ai-agent/preview", json=preview_request)
        assert response.status_code == 200
        
        preview = response.json()
        assert preview["operation"] == "split_task"
        assert preview["confidence_score"] == 0.6  # Fallback confidence
        
        # Verify fallback creates plan-execute-review pattern
        create_action = next(
            change for change in preview["proposed_changes"] 
            if change["action"] == "create_tasks"
        )
        subtasks = create_action["tasks"]
        assert len(subtasks) == 3
        
        titles = [task["title"] for task in subtasks]
        assert any("Plan:" in title for title in titles)
        assert any("Execute:" in title for title in titles)
        assert any("Review:" in title for title in titles)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
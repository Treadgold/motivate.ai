"""
Simplified AI Agent Service

A sophisticated AI agent that uses reasoning chains and function calling
to perform complex operations like task splitting, project definition, etc.
Uses a simple state machine instead of LangGraph to avoid dependency conflicts.
"""

import os
import json
import httpx
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment from shared config
shared_config_path = Path(__file__).parent.parent.parent / "shared" / "config.env.example"
load_dotenv(shared_config_path)
load_dotenv()  # Also load any local .env file


class OperationType(Enum):
    """Supported AI agent operations"""
    SPLIT_TASK = "split_task"
    IMPROVE_DESCRIPTION = "improve_description"
    MERGE_TASKS = "merge_tasks"
    DEFINE_PROJECT = "define_new_project"
    OPTIMIZE_WORKFLOW = "optimize_workflow"
    SUGGEST_PRIORITIES = "suggest_priorities"


@dataclass
class AgentRequest:
    """Request structure for AI agent operations"""
    operation: OperationType
    task_ids: Optional[List[int]] = None
    project_ids: Optional[List[int]] = None
    context: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None


@dataclass
class AgentPreview:
    """Preview of changes before execution"""
    operation: str
    original_data: Dict[str, Any]
    proposed_changes: List[Dict[str, Any]]
    reasoning: str
    confidence_score: float
    estimated_impact: str


@dataclass
class AgentResult:
    """Final result of agent execution"""
    success: bool
    operation: str
    preview: AgentPreview
    executed_changes: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None


class AgentState:
    """State management for the workflow"""
    def __init__(self, request: Dict[str, Any]):
        self.request = request
        self.gathered_data: Dict[str, Any] = {}
        self.analysis: Dict[str, Any] = {}
        self.proposed_changes: List[Dict[str, Any]] = []
        self.reasoning_chain: List[str] = []
        self.confidence_score: float = 0.0
        self.ready_for_preview: bool = False
        self.preview_approved: bool = False
        self.execution_complete: bool = False
        self.error: Optional[str] = None


class AIAgent:
    """Main AI Agent using simple state machine for reasoning workflows"""
    
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("AI_MODEL", "qwen3max:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "600"))
        
        # Initialize tools
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[Dict[str, Any]]:
        """Create function calling tools for the AI agent"""
        
        def get_task_details(task_id: int) -> str:
            """Get comprehensive details about a specific task"""
            try:
                # Try direct database access first (when running in API server)
                try:
                    from database import get_db
                    from models.task import Task
                    db = next(get_db())
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task_dict = {
                            "id": task.id,
                            "project_id": task.project_id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "priority": task.priority,
                            "estimated_minutes": task.estimated_minutes,
                            "actual_minutes": task.actual_minutes,
                            "is_suggestion": task.is_suggestion,
                            "energy_level": task.energy_level,
                            "context": task.context,
                            "is_completed": task.is_completed,
                            "created_at": task.created_at.isoformat() if task.created_at else None,
                            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                            "completed_at": task.completed_at.isoformat() if task.completed_at else None
                        }
                        return json.dumps(task_dict, indent=2)
                    else:
                        return f"Error: Task {task_id} not found"
                except Exception:
                    # Fallback to HTTP request
                    response = httpx.get(f"{self.api_base_url}/tasks/{task_id}", timeout=self.timeout)
                    if response.status_code == 200:
                        return json.dumps(response.json(), indent=2)
                    else:
                        return f"Error: Task {task_id} not found"
            except Exception as e:
                return f"Error fetching task {task_id}: {str(e)}"
        
        def get_project_details(project_id: int) -> str:
            """Get comprehensive details about a specific project"""
            try:
                # Try direct database access first (when running in API server)
                try:
                    from database import get_db
                    from models.project import Project
                    db = next(get_db())
                    project = db.query(Project).filter(Project.id == project_id).first()
                    if project:
                        project_dict = {
                            "id": project.id,
                            "title": project.title,
                            "description": project.description,
                            "location": project.location,
                            "created_at": project.created_at.isoformat() if project.created_at else None,
                            "updated_at": project.updated_at.isoformat() if project.updated_at else None
                        }
                        return json.dumps(project_dict, indent=2)
                    else:
                        return f"Error: Project {project_id} not found"
                except Exception:
                    # Fallback to HTTP request
                    response = httpx.get(f"{self.api_base_url}/projects/{project_id}", timeout=self.timeout)
                    if response.status_code == 200:
                        return json.dumps(response.json(), indent=2)
                    else:
                        return f"Error: Project {project_id} not found"
            except Exception as e:
                return f"Error fetching project {project_id}: {str(e)}"
        
        def get_project_tasks(project_id: int) -> str:
            """Get all tasks for a specific project"""
            try:
                # Try direct database access first (when running in API server)
                try:
                    from database import get_db
                    from models.task import Task
                    db = next(get_db())
                    tasks = db.query(Task).filter(Task.project_id == project_id).all()
                    task_list = []
                    for task in tasks:
                        task_dict = {
                            "id": task.id,
                            "project_id": task.project_id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "priority": task.priority,
                            "estimated_minutes": task.estimated_minutes,
                            "actual_minutes": task.actual_minutes,
                            "is_suggestion": task.is_suggestion,
                            "energy_level": task.energy_level,
                            "context": task.context,
                            "is_completed": task.is_completed,
                            "created_at": task.created_at.isoformat() if task.created_at else None,
                            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                            "completed_at": task.completed_at.isoformat() if task.completed_at else None
                        }
                        task_list.append(task_dict)
                    return json.dumps(task_list, indent=2)
                except Exception:
                    # Fallback to HTTP request
                    response = httpx.get(f"{self.api_base_url}/tasks?project_id={project_id}", timeout=self.timeout)
                    if response.status_code == 200:
                        tasks = response.json()
                        return json.dumps(tasks, indent=2)
                    else:
                        return f"Error: Could not fetch tasks for project {project_id}"
            except Exception as e:
                return f"Error fetching project tasks {project_id}: {str(e)}"
        
        def create_tasks_bulk(tasks_data: str) -> str:
            """Create multiple tasks at once"""
            try:
                tasks_json = json.loads(tasks_data)
                
                # Use direct database access to avoid HTTP deadlock
                try:
                    from database import get_db
                    from models.task import Task
                    db = next(get_db())
                    
                    created_tasks = []
                    for task_data in tasks_json:
                        # Convert to Task model format
                        db_task = Task(
                            project_id=task_data.get('project_id'),
                            title=task_data.get('title'),
                            description=task_data.get('description'),
                            status=task_data.get('status', 'pending'),
                            priority=task_data.get('priority', 'medium'),
                            estimated_minutes=task_data.get('estimated_minutes', 15),
                            energy_level=task_data.get('energy_level', 'medium'),
                            context=task_data.get('context'),
                            is_suggestion=task_data.get('is_suggestion', False)
                        )
                        db.add(db_task)
                        created_tasks.append(db_task)
                    
                    db.commit()
                    
                    # Refresh to get IDs
                    for task in created_tasks:
                        db.refresh(task)
                    
                    # Convert to response format
                    result_tasks = []
                    for task in created_tasks:
                        result_tasks.append({
                            "id": task.id,
                            "project_id": task.project_id,
                            "title": task.title,
                            "description": task.description,
                            "status": task.status,
                            "priority": task.priority,
                            "estimated_minutes": task.estimated_minutes,
                            "actual_minutes": task.actual_minutes,
                            "is_suggestion": task.is_suggestion,
                            "energy_level": task.energy_level,
                            "context": task.context,
                            "is_completed": task.is_completed,
                            "created_at": task.created_at.isoformat() if task.created_at else None,
                            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                            "completed_at": task.completed_at.isoformat() if task.completed_at else None
                        })
                    
                    return json.dumps(result_tasks, indent=2)
                    
                except Exception as db_error:
                    # Fallback to HTTP if database access fails
                    print(f"Database access failed, falling back to HTTP: {str(db_error)}")
                    response = httpx.post(
                        f"{self.api_base_url}/tasks/bulk",
                        json={"tasks": tasks_json},
                        timeout=self.timeout
                    )
                    if response.status_code == 200:
                        return json.dumps(response.json(), indent=2)
                    else:
                        return f"Error creating tasks: {response.status_code} - {response.text}"
                        
            except Exception as e:
                return f"Error creating tasks: {str(e)}"
        
        def delete_task(task_id: int) -> str:
            """Delete a specific task"""
            try:
                # Use direct database access to avoid HTTP deadlock
                try:
                    from database import get_db
                    from models.task import Task
                    db = next(get_db())
                    
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if not task:
                        return f"Error: Task {task_id} not found"
                    
                    db.delete(task)
                    db.commit()
                    return f"Task {task_id} deleted successfully"
                    
                except Exception as db_error:
                    # Fallback to HTTP if database access fails
                    print(f"Database delete failed, falling back to HTTP: {str(db_error)}")
                    response = httpx.delete(f"{self.api_base_url}/tasks/{task_id}", timeout=self.timeout)
                    if response.status_code == 200:
                        return f"Task {task_id} deleted successfully"
                    else:
                        return f"Error deleting task {task_id}: {response.status_code}"
                        
            except Exception as e:
                return f"Error deleting task {task_id}: {str(e)}"
        
        def update_task(task_id: int, updates: str) -> str:
            """Update a specific task"""
            try:
                updates_json = json.loads(updates)
                
                # Try direct database access first (when running in API server)
                try:
                    from database import get_db
                    from models.task import Task
                    from datetime import datetime
                    
                    db = next(get_db())
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if not task:
                        return f"Error: Task {task_id} not found"
                    
                    # Apply updates
                    for field, value in updates_json.items():
                        if hasattr(task, field):
                            setattr(task, field, value)
                    
                    # Handle completion logic
                    if "is_completed" in updates_json:
                        if updates_json["is_completed"] and not task.is_completed:
                            task.completed_at = datetime.utcnow()
                            task.status = "completed"
                        elif not updates_json["is_completed"] and task.is_completed:
                            task.completed_at = None
                            if task.status == "completed":
                                task.status = "pending"
                    
                    db.commit()
                    db.refresh(task)
                    
                    # Return updated task data
                    task_dict = {
                        "id": task.id,
                        "project_id": task.project_id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "estimated_minutes": task.estimated_minutes,
                        "actual_minutes": task.actual_minutes,
                        "is_suggestion": task.is_suggestion,
                        "energy_level": task.energy_level,
                        "context": task.context,
                        "is_completed": task.is_completed,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }
                    return json.dumps(task_dict, indent=2)
                    
                except Exception as db_error:
                    print(f"Database update failed, trying HTTP fallback: {db_error}")
                    # Fallback to HTTP request
                    with httpx.Client(timeout=self.timeout) as client:
                        response = client.put(
                            f"{self.api_base_url}/tasks/{task_id}",
                            json=updates_json
                        )
                    
                    if response.status_code == 200:
                        return json.dumps(response.json(), indent=2)
                    else:
                        return f"Error updating task {task_id}: {response.status_code} - {response.text}"
                        
            except Exception as e:
                return f"Error updating task {task_id}: {str(e)}"
        
        return [
            {
                "name": "get_task_details",
                "description": "Get detailed information about a specific task including title, description, priority, etc.",
                "func": get_task_details
            },
            {
                "name": "get_project_details", 
                "description": "Get detailed information about a specific project",
                "func": get_project_details
            },
            {
                "name": "get_project_tasks",
                "description": "Get all tasks that belong to a specific project",
                "func": get_project_tasks
            },
            {
                "name": "create_tasks_bulk",
                "description": "Create multiple tasks at once. Input should be JSON array of task objects.",
                "func": create_tasks_bulk
            },
            {
                "name": "delete_task",
                "description": "Delete a specific task by ID",
                "func": delete_task
            },
            {
                "name": "update_task",
                "description": "Update a specific task. Input should be JSON object with fields to update.",
                "func": update_task
            }
        ]
    
    def _gather_data(self, state: AgentState) -> None:
        """Gather all necessary data for the operation"""
        operation = state.request.get("operation")
        
        reasoning = f"Starting {operation} operation. Gathering required data..."
        state.reasoning_chain.append(reasoning)
        
        if operation == OperationType.SPLIT_TASK.value:
            task_ids = state.request.get("task_ids", [])
            gathered = {}
            
            for task_id in task_ids:
                # Get task details
                task_tool = next(t for t in self.tools if t["name"] == "get_task_details")
                task_data = task_tool["func"](task_id)
                
                try:
                    task_json = json.loads(task_data)
                    gathered[f"task_{task_id}"] = task_json
                    
                    # Get project context
                    project_id = task_json.get("project_id")
                    if project_id:
                        project_tool = next(t for t in self.tools if t["name"] == "get_project_details")
                        project_data = project_tool["func"](project_id)
                        
                        tasks_tool = next(t for t in self.tools if t["name"] == "get_project_tasks")
                        project_tasks = tasks_tool["func"](project_id)
                        
                        gathered[f"project_{project_id}"] = {
                            "details": json.loads(project_data),
                            "all_tasks": json.loads(project_tasks)
                        }
                
                except json.JSONDecodeError as e:
                    state.error = f"Failed to parse data for task {task_id}: {str(e)}. Raw data: {task_data[:200]}"
                    return
                    
            state.gathered_data = gathered
            state.reasoning_chain.append(f"Gathered data for {len(task_ids)} tasks and their project contexts")
            
        elif operation == OperationType.IMPROVE_DESCRIPTION.value:
            task_ids = state.request.get("task_ids", [])
            gathered = {}
            
            for task_id in task_ids:
                # Get task details
                task_tool = next(t for t in self.tools if t["name"] == "get_task_details")
                task_data = task_tool["func"](task_id)
                
                try:
                    task_json = json.loads(task_data)
                    gathered[f"task_{task_id}"] = task_json
                    
                    # Get project context for better understanding
                    project_id = task_json.get("project_id")
                    if project_id:
                        project_tool = next(t for t in self.tools if t["name"] == "get_project_details")
                        project_data = project_tool["func"](project_id)
                        
                        tasks_tool = next(t for t in self.tools if t["name"] == "get_project_tasks")
                        project_tasks = tasks_tool["func"](project_id)
                        
                        gathered[f"project_{project_id}"] = {
                            "details": json.loads(project_data),
                            "all_tasks": json.loads(project_tasks)
                        }
                
                except json.JSONDecodeError as e:
                    state.error = f"Failed to parse data for task {task_id}: {str(e)}. Raw data: {task_data[:200]}"
                    return
                    
            state.gathered_data = gathered
            state.reasoning_chain.append(f"Gathered data for {len(task_ids)} tasks and their project contexts")
    
    async def _analyze_and_reason(self, state: AgentState) -> None:
        """Perform AI reasoning on the gathered data"""
        operation = state.request.get("operation")
        
        if operation == OperationType.SPLIT_TASK.value:
            # Use AI to analyze and propose task splits
            analysis_result = await self._analyze_task_splitting(state.gathered_data, state.request)
            state.analysis = analysis_result["analysis"]
            state.proposed_changes = analysis_result["proposed_changes"]
            state.confidence_score = analysis_result["confidence_score"]
            state.reasoning_chain.extend(analysis_result["reasoning_steps"])
        elif operation == OperationType.IMPROVE_DESCRIPTION.value:
            # Use AI to analyze and propose description improvements
            analysis_result = await self._analyze_description_improvement(state.gathered_data, state.request)
            state.analysis = analysis_result["analysis"]
            state.proposed_changes = analysis_result["proposed_changes"]
            state.confidence_score = analysis_result["confidence_score"]
            state.reasoning_chain.extend(analysis_result["reasoning_steps"])
        
        state.ready_for_preview = True
    
    def _create_preview(self, state: AgentState) -> None:
        """Create a preview of proposed changes"""
        operation = state.request.get("operation")
        
        # Extract original data for preview
        original_data = {}
        if operation == OperationType.SPLIT_TASK.value:
            task_ids = state.request.get("task_ids", [])
            for task_id in task_ids:
                task_key = f"task_{task_id}"
                if task_key in state.gathered_data:
                    original_data[task_key] = state.gathered_data[task_key]
        elif operation == OperationType.IMPROVE_DESCRIPTION.value:
            task_ids = state.request.get("task_ids", [])
            for task_id in task_ids:
                task_key = f"task_{task_id}"
                if task_key in state.gathered_data:
                    original_data[task_key] = state.gathered_data[task_key]
        
        # Create structured preview
        preview = {
            "operation": operation,
            "original_data": original_data,
            "proposed_changes": state.proposed_changes,
            "reasoning": "\n".join(state.reasoning_chain),
            "confidence_score": state.confidence_score,
            "estimated_impact": state.analysis.get("impact_assessment", "Moderate impact expected")
        }
        
        state.analysis["preview"] = preview
    
    def _execute_changes(self, state: AgentState) -> None:
        """Execute the approved changes"""
        print("Starting task execution...")
        
        if not state.preview_approved:
            state.error = "Cannot execute changes without preview approval"
            return
        
        operation = state.request.get("operation")
        executed_changes = []
        
        try:
            if operation == OperationType.SPLIT_TASK.value:
                print(f"Executing task splitting with {len(state.proposed_changes)} changes...")
                
                # Execute task splitting
                for i, change in enumerate(state.proposed_changes):
                    print(f"Processing change {i+1}/{len(state.proposed_changes)}: {change['action']}")
                    
                    if change["action"] == "create_tasks":
                        print(f"Creating {len(change['tasks'])} new tasks...")
                        
                        # Ensure all tasks have project_id from original task
                        tasks_with_project_id = []
                        
                        # Find the correct project_id from original task data
                        original_project_id = None
                        for key, value in state.gathered_data.items():
                            if key.startswith("task_") and isinstance(value, dict):
                                original_project_id = value.get("project_id")
                                if original_project_id:
                                    break
                        
                        for task_data in change["tasks"]:
                            # Always set the project_id from original task, whether missing or literal string
                            if not task_data.get("project_id") or task_data.get("project_id") == "INHERIT_FROM_ORIGINAL_TASK":
                                if original_project_id:
                                    task_data["project_id"] = original_project_id
                                    print(f"Set project_id {original_project_id} for task: {task_data.get('title', 'Untitled')}")
                                else:
                                    print(f"WARNING: No original project_id found for task: {task_data.get('title', 'Untitled')}")
                            
                            tasks_with_project_id.append(task_data)
                        
                        create_tool = next(t for t in self.tools if t["name"] == "create_tasks_bulk")
                        result = create_tool["func"](json.dumps(tasks_with_project_id))
                        executed_changes.append({
                            "action": "created_tasks",
                            "result": result
                        })
                        print("✓ Tasks created successfully")
                    
                    elif change["action"] == "delete_task":
                        print(f"Deleting task {change['task_id']}...")
                        delete_tool = next(t for t in self.tools if t["name"] == "delete_task")
                        result = delete_tool["func"](change["task_id"])
                        executed_changes.append({
                            "action": "deleted_task",
                            "task_id": change["task_id"],
                            "result": result
                        })
                        print("✓ Task deleted successfully")
                        
            elif operation == OperationType.IMPROVE_DESCRIPTION.value:
                print(f"Executing description improvement with {len(state.proposed_changes)} changes...")
                
                # Execute description improvement
                for i, change in enumerate(state.proposed_changes):
                    print(f"Processing change {i+1}/{len(state.proposed_changes)}: {change['action']}")
                    
                    if change["action"] == "update_task":
                        task_id = change["task_id"]
                        updates = change["updates"]
                        print(f"Updating task {task_id} with updates: {updates}")
                        
                        # Show the new description length for debugging
                        if "description" in updates:
                            new_desc = updates["description"]
                            print(f"New description length: {len(new_desc)} characters")
                            print(f"New description preview: {new_desc[:100]}...")
                        
                        update_tool = next(t for t in self.tools if t["name"] == "update_task")
                        result = update_tool["func"](task_id, json.dumps(updates))
                        
                        # Parse the result to check if update was successful
                        try:
                            result_data = json.loads(result) if isinstance(result, str) else result
                            if isinstance(result_data, dict) and result_data.get("id") == task_id:
                                print(f"✓ CONFIRMED: Task {task_id} description updated in database")
                                print(f"✓ New description length: {len(result_data.get('description', ''))}")
                                print(f"✓ New description preview: {result_data.get('description', '')[:100]}...")
                            else:
                                print(f"⚠️  WARNING: Unexpected update result format: {result}")
                        except Exception as parse_error:
                            print(f"⚠️  WARNING: Could not parse update result: {parse_error}")
                            print(f"Raw result: {result}")
                        
                        executed_changes.append({
                            "action": "updated_task",
                            "task_id": task_id,
                            "updates": updates,
                            "result": result
                        })
                        print(f"✓ Task description update completed. API response: {result[:200]}...")
            
            state.analysis["executed_changes"] = executed_changes
            state.execution_complete = True
            state.reasoning_chain.append("Successfully executed all proposed changes")
            print("✓ All changes executed successfully!")
            
        except Exception as e:
            print(f"✗ Error during execution: {str(e)}")
            state.error = f"Error executing changes: {str(e)}"
    
    async def _analyze_task_splitting(self, gathered_data: Dict, request: Dict) -> Dict[str, Any]:
        """Use AI to analyze task splitting with comprehensive reasoning"""
        
        task_ids = request.get("task_ids", [])
        if not task_ids:
            return {
                "analysis": {"error": "No task IDs provided"},
                "proposed_changes": [],
                "confidence_score": 0.0,
                "reasoning_steps": ["Error: No task IDs provided for splitting"]
            }
        
        # Build comprehensive context
        context_parts = []
        for task_id in task_ids:
            task_key = f"task_{task_id}"
            if task_key in gathered_data:
                task = gathered_data[task_key]
                context_parts.append(f"""
                                    Task to Split (ID: {task_id}):
                                    - Title: {task.get('title', 'N/A')}
                                    - Description: {task.get('description', 'N/A')}
                                    - Priority: {task.get('priority', 'medium')}
                                    - Estimated Time: {task.get('estimated_minutes', 15)} minutes
                                    - Energy Level: {task.get('energy_level', 'medium')}
                                    - Status: {task.get('status', 'pending')}
                                    - Context: {task.get('context', 'N/A')}""")
                
                # Add project context
                project_id = task.get('project_id')
                if project_id and f"project_{project_id}" in gathered_data:
                    project_data = gathered_data[f"project_{project_id}"]
                    project_details = project_data.get("details", {})
                    all_tasks = project_data.get("all_tasks", [])
                    
                    context_parts.append(f"""
                                            Project Context:
                                            - Project: {project_details.get('title', 'N/A')}
                                            - Description: {project_details.get('description', 'N/A')}
                                            - Location: {project_details.get('location', 'N/A')}
                                            - Existing Tasks: {len(all_tasks)} total tasks
                                            - Recent Tasks: {[t.get('title', 'N/A') for t in all_tasks[-3:] if not t.get('is_completed', False)]}""")
        
        context_text = "\n".join(context_parts)
        
        prompt = f"""You are an expert productivity consultant analyzing tasks for optimal splitting.

                    {context_text}

                    Your task is to analyze the given task(s) and determine how to split them into smaller, more manageable subtasks.

                    Please provide your analysis in this exact JSON format:
                    {{
                    "reasoning_steps": [
                        "Step-by-step reasoning about why and how to split this task",
                        "Consider task complexity, time estimates, dependencies, etc."
                    ],
                    "task_splits": [
                        {{
                        "original_task_id": {task_ids[0] if task_ids else 'null'},
                        "subtasks": [
                            {{
                            "title": "Specific subtask title",
                            "description": "Detailed description",
                            "estimated_minutes": 15,
                            "priority": "medium",
                            "energy_level": "medium",
                            "context": "when you have focus",
                            "project_id": "INHERIT_FROM_ORIGINAL_TASK",
                            "reasoning": "Why this subtask is necessary"
                            }}
                        ],
                        "split_rationale": "Overall reason for this particular split approach"
                        }}
                    ],
                    "confidence_score": 0.85,
                    "impact_assessment": "This split will make the work more manageable by...",
                    "recommendations": [
                        "Additional recommendations for task management"
                    ]
                    }}

                    Key principles:
                    1. Each subtask should be 5-20 minutes
                    2. Subtasks should be logically ordered
                    3. Avoid duplicating existing project tasks
                    4. Consider the original task's context and energy requirements
                    5. Ensure subtasks together complete the original task
                    6. Use "INHERIT_FROM_ORIGINAL_TASK" for project_id - it will be automatically set
                    """

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more focused analysis
                            "top_p": 0.9
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # Enhanced cleaning and parsing of AI response
                    clean_response = ai_response.strip()
                    
                    # Remove thinking tags for reasoning models
                    if "<think>" in clean_response and "</think>" in clean_response:
                        start = clean_response.find("</think>") + len("</think>")
                        clean_response = clean_response[start:].strip()
                    
                    # Remove any leading/trailing markdown
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    elif clean_response.startswith("```"):
                        clean_response = clean_response[3:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]
                    clean_response = clean_response.strip()
                    
                    # Try to extract JSON from response if there's extra text
                    json_start = clean_response.find("{")
                    json_end = clean_response.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        clean_response = clean_response[json_start:json_end]
                    
                    analysis_data = json.loads(clean_response)
                    
                    # Convert to our format
                    proposed_changes = []
                    for split in analysis_data.get("task_splits", []):
                        original_task_id = split.get("original_task_id")
                        
                        # Add change to create new subtasks
                        proposed_changes.append({
                            "action": "create_tasks",
                            "tasks": split.get("subtasks", []),
                            "reasoning": split.get("split_rationale", "")
                        })
                        
                        # Add change to delete original task
                        if original_task_id:
                            proposed_changes.append({
                                "action": "delete_task",
                                "task_id": original_task_id,
                                "reasoning": f"Original task replaced by {len(split.get('subtasks', []))} subtasks"
                            })
                    
                    return {
                        "analysis": {
                            "ai_analysis": analysis_data,
                            "impact_assessment": analysis_data.get("impact_assessment", "Moderate impact"),
                            "recommendations": analysis_data.get("recommendations", [])
                        },
                        "proposed_changes": proposed_changes,
                        "confidence_score": analysis_data.get("confidence_score", 0.7),
                        "reasoning_steps": analysis_data.get("reasoning_steps", ["AI analysis completed"])
                    }
                
                else:
                    raise Exception(f"AI API error: {response.status_code}")
                    
        except httpx.ReadTimeout as e:
            print(f"AI analysis timeout after {self.timeout}s - Error: {str(e)}")
            print(f"Consider increasing OLLAMA_TIMEOUT for complex reasoning tasks")
            
            # For timeouts, try a simpler prompt with retry
            return await self._retry_with_simpler_prompt(gathered_data, task_ids)
            
        except httpx.ConnectTimeout as e:
            print(f"AI connection timeout - Error: {str(e)}")
            print("Check if Ollama is running and accessible")
            return self._fallback_task_analysis(gathered_data, task_ids)
            
        except json.JSONDecodeError as e:
            print(f"AI response parsing failed - Error: {str(e)}")
            
            # If we got a response but parsing failed, log the raw response
            if 'ai_response' in locals():
                print(f"Raw AI response (first 500 chars): {ai_response[:500]}...")
                print(f"Clean response (first 500 chars): {clean_response[:500] if 'clean_response' in locals() else 'Not available'}...")
            
            return self._fallback_task_analysis(gathered_data, task_ids)
            
        except Exception as e:
            # Log the actual error before falling back
            print(f"AI analysis failed - Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            
            # If we got a response but parsing failed, log the raw response
            if 'ai_response' in locals():
                print(f"Raw AI response (first 500 chars): {ai_response[:500]}...")
                print(f"Clean response (first 500 chars): {clean_response[:500] if 'clean_response' in locals() else 'Not available'}...")
            
            # Fallback analysis
            return self._fallback_task_analysis(gathered_data, task_ids)
    
    async def _retry_with_simpler_prompt(self, gathered_data: Dict, task_ids: List[int]) -> Dict[str, Any]:
        """Retry with a shorter, simpler prompt for timeout cases"""
        
        if not task_ids:
            return self._fallback_task_analysis(gathered_data, task_ids)
        
        # Build minimal context
        task_summaries = []
        for task_id in task_ids:
            task_key = f"task_{task_id}"
            if task_key in gathered_data:
                task = gathered_data[task_key]
                task_summaries.append(f"Task {task_id}: {task.get('title', 'N/A')} ({task.get('estimated_minutes', 15)}min)")
        
        if not task_summaries:
            return self._fallback_task_analysis(gathered_data, task_ids)
        
        simple_prompt = f"""Split this task into 2-5 smaller subtasks. Return JSON only:

{'; '.join(task_summaries)}

{{
  "task_splits": [{{
    "original_task_id": {task_ids[0]},
    "subtasks": [{{
      "title": "Step name",
      "description": "What to do",
      "estimated_minutes": 10,
      "priority": "medium",
      "energy_level": "medium",
      "context": "when you have time",
      "project_id": "INHERIT_FROM_ORIGINAL_TASK"
    }}],
    "split_rationale": "Why split this way"
  }}],
  "confidence_score": 0.8,
  "reasoning_steps": ["Quick reasoning"]
}}"""

        try:
            async with httpx.AsyncClient(timeout=60) as client:  # Shorter timeout for retry
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": simple_prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "top_p": 0.8}  # More focused settings
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Simple JSON extraction
                    json_start = ai_response.find("{")
                    json_end = ai_response.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        clean_response = ai_response[json_start:json_end]
                        analysis_data = json.loads(clean_response)
                        
                        # Convert to our format
                        proposed_changes = []
                        for split in analysis_data.get("task_splits", []):
                            proposed_changes.append({
                                "action": "create_tasks",
                                "tasks": split.get("subtasks", []),
                                "reasoning": split.get("split_rationale", "")
                            })
                            
                            if split.get("original_task_id"):
                                proposed_changes.append({
                                    "action": "delete_task",
                                    "task_id": split.get("original_task_id"),
                                    "reasoning": f"Replaced by {len(split.get('subtasks', []))} subtasks"
                                })
                        
                        print("AI analysis succeeded on retry with simpler prompt")
                        return {
                            "analysis": {
                                "ai_analysis": analysis_data,
                                "impact_assessment": "Tasks split successfully",
                                "retry_used": True
                            },
                            "proposed_changes": proposed_changes,
                            "confidence_score": analysis_data.get("confidence_score", 0.7),
                            "reasoning_steps": analysis_data.get("reasoning_steps", ["AI retry analysis"])
                        }
                        
        except Exception as e:
            print(f"Retry also failed: {str(e)}")
        
        # Final fallback
        print("Both AI attempts failed, using fallback analysis")
        return self._fallback_task_analysis(gathered_data, task_ids)
    
    async def _analyze_description_improvement(self, gathered_data: Dict, request: Dict) -> Dict[str, Any]:
        """Use AI to analyze and improve task descriptions"""
        
        task_ids = request.get("task_ids", [])
        if not task_ids:
            return {
                "analysis": {"error": "No task IDs provided"},
                "proposed_changes": [],
                "confidence_score": 0.0,
                "reasoning_steps": ["Error: No task IDs provided for description improvement"]
            }
        
        # Build comprehensive context
        context_parts = []
        for task_id in task_ids:
            task_key = f"task_{task_id}"
            if task_key in gathered_data:
                task = gathered_data[task_key]
                context_parts.append(f"""
                                Task to Improve (ID: {task_id}):
                                - Title: {task.get('title', 'N/A')}
                                - Current Description: {task.get('description', 'No description')}
                                - Priority: {task.get('priority', 'medium')}
                                - Estimated Time: {task.get('estimated_minutes', 15)} minutes
                                - Energy Level: {task.get('energy_level', 'medium')}
                                - Status: {task.get('status', 'pending')}
                                - Context: {task.get('context', 'N/A')}""")
                
                # Add project context
                project_id = task.get('project_id')
                if project_id and f"project_{project_id}" in gathered_data:
                    project_data = gathered_data[f"project_{project_id}"]
                    project_details = project_data.get("details", {})
                    all_tasks = project_data.get("all_tasks", [])
                    
                    context_parts.append(f"""
                                            Project Context:
                                            - Project: {project_details.get('title', 'N/A')}
                                            - Description: {project_details.get('description', 'N/A')}
                                            - Location: {project_details.get('location', 'N/A')}
                                            - Existing Tasks: {len(all_tasks)} total tasks
                                            - Related Tasks: {[t.get('title', 'N/A') for t in all_tasks[-5:] if not t.get('is_completed', False)]}""")
        
        context_text = "\n".join(context_parts)
        
        prompt = f"""You are an expert productivity consultant specializing in creating clear, actionable task descriptions.

                    {context_text}

                    Your task is to analyze the given task(s) and improve their descriptions to make them more actionable, detailed, and easier to execute.

                    Please provide your analysis in this exact JSON format:
                    {{
                    "reasoning_steps": [
                        "Step-by-step analysis of current description quality",
                        "Identify what's missing or unclear",
                        "Explain how improvements will help with execution"
                    ],
                    "task_improvements": [
                        {{
                        "task_id": {task_ids[0] if task_ids else 'null'},
                        "current_description": "Current task description",
                        "improved_description": "Enhanced, actionable description with specific steps, success criteria, and context",
                        "improvement_rationale": "Why this improved description is better",
                        "key_additions": [
                            "What specific information was added",
                            "Clarifications made to execution steps",
                            "Success criteria or completion indicators"
                        ]
                        }}
                    ],
                    "confidence_score": 0.85,
                    "impact_assessment": "This improved description will help by...",
                    "recommendations": [
                        "Additional suggestions for task management or execution"
                    ]
                    }}

                    Key principles for description improvement:
                    1. Add specific action steps when missing
                    2. Include success criteria or completion indicators
                    3. Clarify any ambiguous terms or requirements
                    4. Add relevant context or prerequisites
                    5. Make the task more self-contained and actionable
                    6. Maintain the original scope while adding clarity
                    """

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more focused analysis
                            "top_p": 0.9
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # Enhanced cleaning and parsing of AI response
                    clean_response = ai_response.strip()
                    
                    # Remove thinking tags for reasoning models
                    if "<think>" in clean_response and "</think>" in clean_response:
                        start = clean_response.find("</think>") + len("</think>")
                        clean_response = clean_response[start:].strip()
                    
                    # Remove any leading/trailing markdown
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    elif clean_response.startswith("```"):
                        clean_response = clean_response[3:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]
                    clean_response = clean_response.strip()
                    
                    # Try to extract JSON from response if there's extra text
                    json_start = clean_response.find("{")
                    json_end = clean_response.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        clean_response = clean_response[json_start:json_end]
                    
                    analysis_data = json.loads(clean_response)
                    
                    # Convert to our format
                    proposed_changes = []
                    for improvement in analysis_data.get("task_improvements", []):
                        proposed_changes.append({
                            "action": "update_task",
                            "task_id": improvement.get("task_id"),
                            "updates": {
                                "description": improvement.get("improved_description", "")
                            },
                            "rationale": improvement.get("improvement_rationale", ""),
                            "key_additions": improvement.get("key_additions", [])
                        })
                    
                    return {
                        "analysis": analysis_data,
                        "proposed_changes": proposed_changes,
                        "confidence_score": analysis_data.get("confidence_score", 0.75),
                        "reasoning_steps": analysis_data.get("reasoning_steps", ["AI analysis completed"])
                    }
                else:
                    print(f"AI service error: {response.status_code}")
                    return self._fallback_description_analysis(gathered_data, task_ids)
                    
        except json.JSONDecodeError as e:
            print(f"AI response parsing failed - Error: {str(e)}")
            return self._fallback_description_analysis(gathered_data, task_ids)
            
        except Exception as e:
            print(f"AI analysis failed - Error: {str(e)}")
            return self._fallback_description_analysis(gathered_data, task_ids)

    def _fallback_description_analysis(self, gathered_data: Dict, task_ids: List[int]) -> Dict[str, Any]:
        """Fallback description improvement when AI analysis fails"""
        proposed_changes = []
        
        for task_id in task_ids:
            task_key = f"task_{task_id}"
            if task_key in gathered_data:
                task = gathered_data[task_key]
                current_desc = task.get("description", "")
                
                # Create a basic improved description
                title = task.get("title", "Task")
                improved_desc = current_desc
                
                if not current_desc or len(current_desc.strip()) < 10:
                    improved_desc = f"Complete {title.lower()}. Steps: 1) Review requirements 2) Execute the task 3) Verify completion."
                else:
                    # Add basic improvements
                    if not any(keyword in current_desc.lower() for keyword in ["step", "goal", "complete", "result"]):
                        improved_desc += f"\n\nGoal: Successfully complete {title.lower()}.\nSuccess criteria: Task is finished and meets requirements."
                
                proposed_changes.append({
                    "action": "update_task",
                    "task_id": task_id,
                    "updates": {
                        "description": improved_desc
                    },
                    "rationale": "Basic description enhancement with clearer structure",
                    "key_additions": ["Added success criteria", "Improved clarity"]
                })
        
        return {
            "analysis": {
                "impact_assessment": "Basic description improvements to add clarity and structure"
            },
            "proposed_changes": proposed_changes,
            "confidence_score": 0.6,
            "reasoning_steps": ["Fallback analysis: Enhanced descriptions with basic improvements"]
        }
    
    def _fallback_task_analysis(self, gathered_data: Dict, task_ids: List[int]) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        
        proposed_changes = []
        reasoning_steps = ["Both AI attempts failed, using rule-based fallback analysis"]
        
        for task_id in task_ids:
            task_key = f"task_{task_id}"
            if task_key in gathered_data:
                task = gathered_data[task_key]
                title = task.get("title", "Untitled Task")
                estimated_time = task.get("estimated_minutes", 15)
                
                # Create simple 3-part split
                subtask_time = max(5, estimated_time // 3)
                
                subtasks = [
                    {
                        "title": f"Plan: {title}",
                        "description": f"Plan the approach for '{title}'",
                        "estimated_minutes": subtask_time,
                        "priority": task.get("priority", "medium"),
                        "energy_level": "low",
                        "context": "when you need to get started",
                        "project_id": task.get("project_id")
                    },
                    {
                        "title": f"Execute: {title}",
                        "description": f"Perform the main work for '{title}'",
                        "estimated_minutes": subtask_time,
                        "priority": task.get("priority", "medium"),
                        "energy_level": task.get("energy_level", "medium"),
                        "context": task.get("context", "when you have focus"),
                        "project_id": task.get("project_id")
                    },
                    {
                        "title": f"Review: {title}",
                        "description": f"Complete and review '{title}'",
                        "estimated_minutes": subtask_time,
                        "priority": task.get("priority", "medium"),
                        "energy_level": "medium",
                        "context": "anytime",
                        "project_id": task.get("project_id")
                    }
                ]
                
                proposed_changes.append({
                    "action": "create_tasks",
                    "tasks": subtasks,
                    "reasoning": f"Fallback split of '{title}' into plan-execute-review pattern"
                })
                
                proposed_changes.append({
                    "action": "delete_task",
                    "task_id": task_id,
                    "reasoning": "Original task replaced by structured subtasks"
                })
                
                reasoning_steps.append(f"Split '{title}' using plan-execute-review pattern")
        
        return {
            "analysis": {
                "method": "fallback",
                "impact_assessment": "Basic task splitting applied",
                "recommendations": ["Consider enabling AI service for more sophisticated analysis"]
            },
            "proposed_changes": proposed_changes,
            "confidence_score": 0.6,
            "reasoning_steps": reasoning_steps
        }
    
    async def process_request(self, request: AgentRequest) -> AgentPreview:
        """Process an agent request and return a preview"""
        
        # Convert request to state
        state = AgentState({
            "operation": request.operation.value,
            "task_ids": request.task_ids or [],
            "project_ids": request.project_ids or [],
            "context": request.context or {},
            "user_preferences": request.user_preferences or {}
        })
        
        # Execute workflow steps
        self._gather_data(state)
        if state.error:
            raise Exception(state.error)
        
        await self._analyze_and_reason(state)
        if state.error:
            raise Exception(state.error)
        
        self._create_preview(state)
        
        preview_data = state.analysis.get("preview", {})
        
        return AgentPreview(
            operation=preview_data.get("operation", request.operation.value),
            original_data=preview_data.get("original_data", {}),
            proposed_changes=preview_data.get("proposed_changes", []),
            reasoning=preview_data.get("reasoning", ""),
            confidence_score=preview_data.get("confidence_score", 0.0),
            estimated_impact=preview_data.get("estimated_impact", "Unknown impact")
        )
    
    async def execute_approved_preview(self, preview: AgentPreview) -> AgentResult:
        """Execute a previously approved preview"""
        
        # Recreate the state for execution
        state = AgentState({
            "operation": preview.operation,
            "task_ids": [],  # Will be extracted from original_data
            "project_ids": [],
            "context": {},
            "user_preferences": {}
        })
        
        state.gathered_data = preview.original_data
        state.proposed_changes = preview.proposed_changes
        state.confidence_score = preview.confidence_score
        state.preview_approved = True  # Mark as approved for execution
        
        # Execute changes
        self._execute_changes(state)
        
        if state.error:
            return AgentResult(
                success=False,
                operation=preview.operation,
                preview=preview,
                error_message=state.error
            )
        
        return AgentResult(
            success=True,
            operation=preview.operation,
            preview=preview,
            executed_changes=state.analysis.get("executed_changes", [])
        )


# Global agent instance
_agent_instance = None

def get_ai_agent() -> AIAgent:
    """Get the global AI agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AIAgent()
    return _agent_instance 
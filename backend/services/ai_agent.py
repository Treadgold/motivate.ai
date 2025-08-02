"""
AI Agent Service using LangGraph

A sophisticated AI agent that uses reasoning chains and function calling
to perform complex operations like task splitting, project definition, etc.
Uses LangGraph for structured workflows and decision making.
"""

import os
import json
import httpx
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_core.pydantic_v1 import BaseModel, Field

load_dotenv()


class OperationType(Enum):
    """Supported AI agent operations"""
    SPLIT_TASK = "split_task"
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


class AgentState(BaseModel):
    """State management for LangGraph workflow"""
    request: Dict[str, Any]
    gathered_data: Dict[str, Any] = Field(default_factory=dict)
    analysis: Dict[str, Any] = Field(default_factory=dict)
    proposed_changes: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_chain: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    ready_for_preview: bool = False
    preview_approved: bool = False
    execution_complete: bool = False
    error: Optional[str] = None


class AIAgent:
    """Main AI Agent using LangGraph for complex reasoning workflows"""
    
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("AI_MODEL", "qwen3max:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Initialize LangGraph workflow
        self.workflow = self._create_workflow()
    
    def _create_tools(self) -> List[Tool]:
        """Create function calling tools for the AI agent"""
        
        def get_task_details(task_id: int) -> str:
            """Get comprehensive details about a specific task"""
            try:
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
                response = httpx.put(
                    f"{self.api_base_url}/tasks/{task_id}",
                    json=updates_json,
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return json.dumps(response.json(), indent=2)
                else:
                    return f"Error updating task {task_id}: {response.status_code}"
            except Exception as e:
                return f"Error updating task {task_id}: {str(e)}"
        
        return [
            Tool(
                name="get_task_details",
                description="Get detailed information about a specific task including title, description, priority, etc.",
                func=get_task_details
            ),
            Tool(
                name="get_project_details", 
                description="Get detailed information about a specific project",
                func=get_project_details
            ),
            Tool(
                name="get_project_tasks",
                description="Get all tasks that belong to a specific project",
                func=get_project_tasks
            ),
            Tool(
                name="create_tasks_bulk",
                description="Create multiple tasks at once. Input should be JSON array of task objects.",
                func=create_tasks_bulk
            ),
            Tool(
                name="delete_task",
                description="Delete a specific task by ID",
                func=delete_task
            ),
            Tool(
                name="update_task",
                description="Update a specific task. Input should be JSON object with fields to update.",
                func=update_task
            )
        ]
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for AI agent reasoning"""
        
        def gather_data_node(state: AgentState) -> AgentState:
            """Gather all necessary data for the operation"""
            request = state.request
            operation = request.get("operation")
            
            reasoning = f"Starting {operation} operation. Gathering required data..."
            state.reasoning_chain.append(reasoning)
            
            if operation == OperationType.SPLIT_TASK.value:
                task_ids = request.get("task_ids", [])
                gathered = {}
                
                for task_id in task_ids:
                    # Get task details
                    task_tool = next(t for t in self.tools if t.name == "get_task_details")
                    task_data = task_tool.func(task_id)
                    
                    try:
                        task_json = json.loads(task_data)
                        gathered[f"task_{task_id}"] = task_json
                        
                        # Get project context
                        project_id = task_json.get("project_id")
                        if project_id:
                            project_tool = next(t for t in self.tools if t.name == "get_project_details")
                            project_data = project_tool.func(project_id)
                            
                            tasks_tool = next(t for t in self.tools if t.name == "get_project_tasks")
                            project_tasks = tasks_tool.func(project_id)
                            
                            gathered[f"project_{project_id}"] = {
                                "details": json.loads(project_data),
                                "all_tasks": json.loads(project_tasks)
                            }
                    
                    except json.JSONDecodeError:
                        state.error = f"Failed to parse data for task {task_id}"
                        return state
                
                state.gathered_data = gathered
                state.reasoning_chain.append(f"Gathered data for {len(task_ids)} tasks and their project contexts")
            
            return state
        
        async def analyze_and_reason_node(state: AgentState) -> AgentState:
            """Perform AI reasoning on the gathered data"""
            operation = state.request.get("operation")
            
            if operation == OperationType.SPLIT_TASK.value:
                # Use AI to analyze and propose task splits
                analysis_result = await self._analyze_task_splitting(state.gathered_data, state.request)
                state.analysis = analysis_result["analysis"]
                state.proposed_changes = analysis_result["proposed_changes"]
                state.confidence_score = analysis_result["confidence_score"]
                state.reasoning_chain.extend(analysis_result["reasoning_steps"])
            
            state.ready_for_preview = True
            return state
        
        def create_preview_node(state: AgentState) -> AgentState:
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
            return state
        
        def execute_changes_node(state: AgentState) -> AgentState:
            """Execute the approved changes"""
            if not state.preview_approved:
                state.error = "Cannot execute changes without preview approval"
                return state
            
            operation = state.request.get("operation")
            executed_changes = []
            
            try:
                if operation == OperationType.SPLIT_TASK.value:
                    # Execute task splitting
                    for change in state.proposed_changes:
                        if change["action"] == "create_tasks":
                            create_tool = next(t for t in self.tools if t.name == "create_tasks_bulk")
                            result = create_tool.func(json.dumps(change["tasks"]))
                            executed_changes.append({
                                "action": "created_tasks",
                                "result": result
                            })
                        
                        elif change["action"] == "delete_task":
                            delete_tool = next(t for t in self.tools if t.name == "delete_task")
                            result = delete_tool.func(change["task_id"])
                            executed_changes.append({
                                "action": "deleted_task",
                                "task_id": change["task_id"],
                                "result": result
                            })
                
                state.analysis["executed_changes"] = executed_changes
                state.execution_complete = True
                state.reasoning_chain.append("Successfully executed all proposed changes")
                
            except Exception as e:
                state.error = f"Error executing changes: {str(e)}"
            
            return state
        
        # Build the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("gather_data", gather_data_node)
        workflow.add_node("analyze_and_reason", analyze_and_reason_node)
        workflow.add_node("create_preview", create_preview_node)
        workflow.add_node("execute_changes", execute_changes_node)
        
        # Add edges
        workflow.add_edge("gather_data", "analyze_and_reason")
        workflow.add_edge("analyze_and_reason", "create_preview")
        workflow.add_edge("create_preview", END)  # Stop at preview for user approval
        workflow.add_edge("execute_changes", END)
        
        # Set entry point
        workflow.set_entry_point("gather_data")
        
        return workflow.compile()
    
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
    
    def _fallback_task_analysis(self, gathered_data: Dict, task_ids: List[int]) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        
        proposed_changes = []
        reasoning_steps = ["AI unavailable, using fallback analysis"]
        
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
        initial_state = AgentState(
            request={
                "operation": request.operation.value,
                "task_ids": request.task_ids or [],
                "project_ids": request.project_ids or [],
                "context": request.context or {},
                "user_preferences": request.user_preferences or {}
            }
        )
        
        # Run workflow until preview
        final_state = self.workflow.invoke(initial_state)
        
        if final_state.error:
            raise Exception(final_state.error)
        
        preview_data = final_state.analysis.get("preview", {})
        
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
        initial_state = AgentState(
            request={
                "operation": preview.operation,
                "task_ids": [],  # Will be extracted from original_data
                "project_ids": [],
                "context": {},
                "user_preferences": {}
            },
            gathered_data=preview.original_data,
            proposed_changes=preview.proposed_changes,
            confidence_score=preview.confidence_score,
            preview_approved=True  # Mark as approved for execution
        )
        
        # Create and execute a simple execution workflow
        def execute_changes_node(state: AgentState) -> AgentState:
            """Execute the approved changes"""
            if not state.preview_approved:
                state.error = "Cannot execute changes without preview approval"
                return state
            
            operation = preview.operation
            executed_changes = []
            
            try:
                if operation == OperationType.SPLIT_TASK.value:
                    # Execute task splitting
                    for change in state.proposed_changes:
                        if change["action"] == "create_tasks":
                            create_tool = next(t for t in self.tools if t.name == "create_tasks_bulk")
                            result = create_tool.func(json.dumps(change["tasks"]))
                            executed_changes.append({
                                "action": "created_tasks",
                                "result": result
                            })
                        
                        elif change["action"] == "delete_task":
                            delete_tool = next(t for t in self.tools if t.name == "delete_task")
                            result = delete_tool.func(change["task_id"])
                            executed_changes.append({
                                "action": "deleted_task",
                                "task_id": change["task_id"],
                                "result": result
                            })
                
                state.analysis["executed_changes"] = executed_changes
                state.execution_complete = True
                state.reasoning_chain.append("Successfully executed all proposed changes")
                
            except Exception as e:
                state.error = f"Error executing changes: {str(e)}"
            
            return state
        
        # Execute directly
        final_state = execute_changes_node(initial_state)
        
        if final_state.error:
            return AgentResult(
                success=False,
                operation=preview.operation,
                preview=preview,
                error_message=final_state.error
            )
        
        return AgentResult(
            success=True,
            operation=preview.operation,
            preview=preview,
            executed_changes=final_state.analysis.get("executed_changes", [])
        )


# Global agent instance
_agent_instance = None

def get_ai_agent() -> AIAgent:
    """Get the global AI agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AIAgent()
    return _agent_instance 
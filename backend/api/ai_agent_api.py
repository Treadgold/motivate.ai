"""
AI Agent API Endpoints

Provides REST API endpoints for AI agent operations including
task splitting, project definition, and workflow optimization.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from services.ai_agent_simple import AIAgent, AgentRequest, AgentPreview, AgentResult, OperationType, get_ai_agent

router = APIRouter(tags=["ai-agent"])


# Request/Response Schemas
class AgentOperationRequest(BaseModel):
    """Request for AI agent operation"""
    operation: str  # "split_task", "merge_tasks", "define_new_project", etc.
    task_ids: Optional[List[int]] = None
    project_ids: Optional[List[int]] = None
    context: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None


class PreviewResponse(BaseModel):
    """Response containing operation preview"""
    operation: str
    original_data: Dict[str, Any]
    proposed_changes: List[Dict[str, Any]]
    reasoning: str
    confidence_score: float
    estimated_impact: str
    preview_id: str  # For tracking when executing


class ExecutionResponse(BaseModel):
    """Response after executing an approved preview"""
    success: bool
    operation: str
    executed_changes: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    execution_id: str


# Global storage for previews (in production, use Redis or database)
_preview_storage: Dict[str, AgentPreview] = {}


def generate_preview_id() -> str:
    """Generate a unique ID for preview tracking"""
    import uuid
    return str(uuid.uuid4())


@router.post("/ai-agent/preview", response_model=PreviewResponse)
async def create_agent_preview(
    request: AgentOperationRequest,
    db: Session = Depends(get_db)
):
    """
    Create a preview of AI agent operations without executing them
    
    This endpoint allows users to see what the AI agent plans to do
    before actually making changes to their data.
    """
    
    try:
        # Validate operation type
        try:
            operation_type = OperationType(request.operation)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported operation: {request.operation}. "
                       f"Supported operations: {[op.value for op in OperationType]}"
            )
        
        # Validate required inputs based on operation
        if operation_type == OperationType.SPLIT_TASK:
            if not request.task_ids or len(request.task_ids) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="task_ids are required for split_task operation"
                )
        
        # Create agent request
        agent_request = AgentRequest(
            operation=operation_type,
            task_ids=request.task_ids,
            project_ids=request.project_ids,
            context=request.context,
            user_preferences=request.user_preferences
        )
        
        # Get AI agent and process request
        agent = get_ai_agent()
        preview = await agent.process_request(agent_request)
        
        # Generate preview ID and store
        preview_id = generate_preview_id()
        _preview_storage[preview_id] = preview
        
        return PreviewResponse(
            operation=preview.operation,
            original_data=preview.original_data,
            proposed_changes=preview.proposed_changes,
            reasoning=preview.reasoning,
            confidence_score=preview.confidence_score,
            estimated_impact=preview.estimated_impact,
            preview_id=preview_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create preview: {str(e)}"
        )


@router.post("/ai-agent/execute/{preview_id}", response_model=ExecutionResponse)
async def execute_agent_preview(
    preview_id: str,
    db: Session = Depends(get_db)
):
    """
    Execute a previously generated and approved preview
    
    This endpoint takes a preview ID and executes the planned changes,
    making actual modifications to the data.
    """
    
    try:
        # Retrieve stored preview
        if preview_id not in _preview_storage:
            raise HTTPException(
                status_code=404,
                detail=f"Preview {preview_id} not found or expired"
            )
        
        preview = _preview_storage[preview_id]
        
        # Get AI agent and execute
        agent = get_ai_agent()
        result = await agent.execute_approved_preview(preview)
        
        # Clean up storage
        del _preview_storage[preview_id]
        
        # Generate execution ID
        import uuid
        execution_id = str(uuid.uuid4())
        
        return ExecutionResponse(
            success=result.success,
            operation=result.operation,
            executed_changes=result.executed_changes,
            error_message=result.error_message,
            execution_id=execution_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute preview: {str(e)}"
        )


@router.delete("/ai-agent/preview/{preview_id}")
async def cancel_agent_preview(preview_id: str):
    """
    Cancel a preview without executing it
    
    This endpoint allows users to discard a preview they don't want to execute.
    """
    
    if preview_id not in _preview_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Preview {preview_id} not found"
        )
    
    del _preview_storage[preview_id]
    
    return {"message": f"Preview {preview_id} cancelled successfully"}


@router.get("/ai-agent/operations")
async def get_supported_operations():
    """
    Get list of supported AI agent operations
    
    Returns information about what operations the AI agent can perform.
    """
    
    operations = []
    for op in OperationType:
        operation_info = {
            "name": op.value,
            "description": "",
            "required_inputs": [],
            "optional_inputs": []
        }
        
        if op == OperationType.SPLIT_TASK:
            operation_info.update({
                "description": "Split complex tasks into smaller, manageable subtasks",
                "required_inputs": ["task_ids"],
                "optional_inputs": ["context", "user_preferences"]
            })
        elif op == OperationType.MERGE_TASKS:
            operation_info.update({
                "description": "Merge related tasks into a single unified task",
                "required_inputs": ["task_ids"],
                "optional_inputs": ["context", "user_preferences"]
            })
        elif op == OperationType.DEFINE_PROJECT:
            operation_info.update({
                "description": "Help define and structure a new project with initial tasks",
                "required_inputs": ["context"],
                "optional_inputs": ["user_preferences"]
            })
        elif op == OperationType.OPTIMIZE_WORKFLOW:
            operation_info.update({
                "description": "Analyze and optimize task workflows for better productivity",
                "required_inputs": ["project_ids"],
                "optional_inputs": ["task_ids", "context", "user_preferences"]
            })
        elif op == OperationType.SUGGEST_PRIORITIES:
            operation_info.update({
                "description": "Suggest task priorities based on deadlines, dependencies, and importance",
                "required_inputs": ["project_ids"],
                "optional_inputs": ["task_ids", "context", "user_preferences"]
            })
        
        operations.append(operation_info)
    
    return {
        "supported_operations": operations,
        "total_operations": len(operations)
    }


@router.get("/ai-agent/status")
async def get_agent_status():
    """
    Get the current status of the AI agent system
    
    Returns information about agent availability, active previews, etc.
    """
    
    try:
        agent = get_ai_agent()
        
        # Test agent connectivity (simple check)
        test_tools = len(agent.tools) > 0
        
        return {
            "status": "online" if test_tools else "degraded",
            "tools_available": len(agent.tools),
            "active_previews": len(_preview_storage),
            "supported_operations": len(OperationType),
            "ai_backend": "ollama",
            "workflow_engine": "langgraph"
        }
        
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "active_previews": len(_preview_storage)
        }


@router.get("/ai-agent/preview/{preview_id}")
async def get_preview_details(preview_id: str):
    """
    Get details of a specific preview
    
    Allows checking the contents of a preview before deciding to execute or cancel.
    """
    
    if preview_id not in _preview_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Preview {preview_id} not found"
        )
    
    preview = _preview_storage[preview_id]
    
    return {
        "preview_id": preview_id,
        "operation": preview.operation,
        "original_data": preview.original_data,
        "proposed_changes": preview.proposed_changes,
        "reasoning": preview.reasoning,
        "confidence_score": preview.confidence_score,
        "estimated_impact": preview.estimated_impact,
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending_approval"
    } 
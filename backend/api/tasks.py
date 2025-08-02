from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.task import Task

router = APIRouter(tags=["tasks"])

# Enhanced Pydantic schemas
class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    estimated_minutes: int = 15
    energy_level: str = "medium"
    context: Optional[str] = None
    is_suggestion: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    energy_level: Optional[str] = None
    context: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    estimated_minutes: int
    actual_minutes: int
    is_suggestion: bool
    energy_level: str
    context: Optional[str] = None
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BulkTaskCreate(BaseModel):
    tasks: List[TaskCreate]

class TaskSplitResponse(BaseModel):
    original_task: TaskResponse
    suggested_tasks: List[TaskCreate]

# Basic routes
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all tasks, optionally filtered by project_id"""
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    tasks = query.all()
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task by ID"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/tasks/bulk", response_model=List[TaskResponse])
async def create_tasks_bulk(bulk_tasks: BulkTaskCreate, db: Session = Depends(get_db)):
    """Create multiple tasks at once"""
    created_tasks = []
    for task_data in bulk_tasks.tasks:
        db_task = Task(**task_data.dict())
        db.add(db_task)
        created_tasks.append(db_task)
    
    db.commit()
    
    # Refresh all created tasks
    for task in created_tasks:
        db.refresh(task)
    
    return created_tasks

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # Handle completion logic
    if task.is_completed is not None:
        if task.is_completed and not db_task.is_completed:
            db_task.completed_at = datetime.utcnow()
            db_task.status = "completed"
        elif not task.is_completed and db_task.is_completed:
            db_task.completed_at = None
            if db_task.status == "completed":
                db_task.status = "pending"
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as completed"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.is_completed = True
    db_task.status = "completed"
    db_task.completed_at = datetime.utcnow()
    db.commit()
    return {"message": "Task completed successfully"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.post("/tasks/{task_id}/split", response_model=TaskSplitResponse)
async def split_task(task_id: int, db: Session = Depends(get_db)):
    """Split a task into smaller tasks using AI assistance"""
    from services.ai_service import AIService
    
    # Get the original task
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Use AI service to generate subtasks
    ai_service = AIService()
    try:
        suggested_subtasks = await ai_service.split_task_into_subtasks(task_id, db)
        
        # Convert AI suggestions to TaskCreate objects
        task_creates = []
        for subtask in suggested_subtasks:
            task_create = TaskCreate(
                project_id=db_task.project_id,
                title=subtask.get("title", "Untitled Subtask"),
                description=subtask.get("description", ""),
                estimated_minutes=subtask.get("estimated_minutes", 15),
                energy_level=subtask.get("energy_level", "medium"),
                context=subtask.get("context", ""),
                priority=db_task.priority,  # Inherit from parent
                is_suggestion=True
            )
            task_creates.append(task_create)
        
        return TaskSplitResponse(
            original_task=db_task,
            suggested_tasks=task_creates
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to split task: {str(e)}") 
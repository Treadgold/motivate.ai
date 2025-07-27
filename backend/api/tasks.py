from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.task import Task

router = APIRouter(tags=["tasks"])

# Pydantic schemas (basic version for now)
class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: str = None
    estimated_minutes: int = 15
    energy_level: str = "medium"

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str = None
    status: str
    estimated_minutes: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Basic routes
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(project_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    tasks = query.all()
    return tasks

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.is_completed = True
    db_task.status = "completed"
    db_task.completed_at = datetime.utcnow()
    db.commit()
    return {"message": "Task completed successfully"} 
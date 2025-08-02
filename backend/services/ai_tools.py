"""
AI Tools Service for Task Management

Provides AI-callable functions for interacting with tasks and projects.
These functions are designed to be used by the AI service for task splitting
and other AI-assisted operations.
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.task import Task
from models.project import Project


class AITaskTools:
    """AI-callable tools for task management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_task_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific task
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Dictionary with task details or None if not found
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
            
        # Get project info for context
        project = self.db.query(Project).filter(Project.id == task.project_id).first()
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "priority": task.priority,
            "estimated_minutes": task.estimated_minutes,
            "actual_minutes": task.actual_minutes,
            "energy_level": task.energy_level,
            "context": task.context or "",
            "is_completed": task.is_completed,
            "is_suggestion": task.is_suggestion,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "project": {
                "id": project.id if project else None,
                "title": project.title if project else "Unknown Project",
                "description": project.description if project else "",
                "location": project.location if project else "",
                "next_action": project.next_action if project else ""
            }
        }
    
    def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all tasks for a specific project
        
        Args:
            project_id: The ID of the project
            
        Returns:
            List of task dictionaries
        """
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "status": task.status,
                "priority": task.priority,
                "estimated_minutes": task.estimated_minutes,
                "energy_level": task.energy_level,
                "context": task.context or "",
                "is_completed": task.is_completed,
                "is_suggestion": task.is_suggestion
            })
        
        return task_list
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Dictionary with created task details
        """
        # Create new task with provided data
        new_task = Task(
            project_id=task_data.get("project_id"),
            title=task_data.get("title", "Untitled Task"),
            description=task_data.get("description", ""),
            status=task_data.get("status", "pending"),
            priority=task_data.get("priority", "medium"),
            estimated_minutes=task_data.get("estimated_minutes", 15),
            energy_level=task_data.get("energy_level", "medium"),
            context=task_data.get("context", ""),
            is_suggestion=task_data.get("is_suggestion", False)
        )
        
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        
        return {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "status": new_task.status,
            "priority": new_task.priority,
            "estimated_minutes": new_task.estimated_minutes,
            "energy_level": new_task.energy_level,
            "context": new_task.context,
            "is_suggestion": new_task.is_suggestion,
            "created_at": new_task.created_at.isoformat() if new_task.created_at else None
        }
    
    def create_multiple_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple tasks at once
        
        Args:
            tasks_data: List of task data dictionaries
            
        Returns:
            List of created task dictionaries
        """
        created_tasks = []
        
        for task_data in tasks_data:
            new_task = Task(
                project_id=task_data.get("project_id"),
                title=task_data.get("title", "Untitled Task"),
                description=task_data.get("description", ""),
                status=task_data.get("status", "pending"),
                priority=task_data.get("priority", "medium"),
                estimated_minutes=task_data.get("estimated_minutes", 15),
                energy_level=task_data.get("energy_level", "medium"),
                context=task_data.get("context", ""),
                is_suggestion=task_data.get("is_suggestion", False)
            )
            
            self.db.add(new_task)
            created_tasks.append(new_task)
        
        self.db.commit()
        
        # Refresh all tasks and return data
        result_tasks = []
        for task in created_tasks:
            self.db.refresh(task)
            result_tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "estimated_minutes": task.estimated_minutes,
                "energy_level": task.energy_level,
                "context": task.context,
                "is_suggestion": task.is_suggestion,
                "created_at": task.created_at.isoformat() if task.created_at else None
            })
        
        return result_tasks
    
    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing task
        
        Args:
            task_id: The ID of the task to update
            updates: Dictionary containing fields to update
            
        Returns:
            Dictionary with updated task details or None if not found
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
        
        # Handle completion logic
        if "is_completed" in updates:
            if updates["is_completed"] and not task.is_completed:
                task.completed_at = datetime.utcnow()
                task.status = "completed"
            elif not updates["is_completed"] and task.is_completed:
                task.completed_at = None
                if task.status == "completed":
                    task.status = "pending"
        
        self.db.commit()
        self.db.refresh(task)
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "estimated_minutes": task.estimated_minutes,
            "energy_level": task.energy_level,
            "context": task.context,
            "is_completed": task.is_completed,
            "is_suggestion": task.is_suggestion
        }
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True
    
    def get_project_context(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get context information about a project for AI analysis
        
        Args:
            project_id: The ID of the project
            
        Returns:
            Dictionary with project context or None if not found
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Get task statistics
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.is_completed])
        pending_tasks = total_tasks - completed_tasks
        
        return {
            "id": project.id,
            "title": project.title,
            "description": project.description or "",
            "location": project.location or "",
            "next_action": project.next_action or "",
            "priority": project.priority,
            "estimated_time": project.estimated_time,
            "tags": project.tags or "",
            "task_stats": {
                "total": total_tasks,
                "completed": completed_tasks,
                "pending": pending_tasks
            }
        }


def get_ai_tools(db: Session = None) -> AITaskTools:
    """
    Get an instance of AI task tools
    
    Args:
        db: Database session (if None, will get a new one)
        
    Returns:
        AITaskTools instance
    """
    if db is None:
        db = next(get_db())
    
    return AITaskTools(db) 
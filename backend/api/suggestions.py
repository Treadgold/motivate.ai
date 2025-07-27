from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models.project import Project
from models.task import Task
from services.ai_service import AIService

router = APIRouter(tags=["suggestions"])
ai_service = AIService()

class SuggestionResponse(BaseModel):
    title: str
    description: str
    estimated_minutes: int
    energy_level: str
    context: str = None
    reasoning: str = None

@router.get("/suggestions/{project_id}", response_model=List[SuggestionResponse])
async def get_project_suggestions(project_id: int, db: Session = Depends(get_db)):
    """Generate AI suggestions for a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Use AI service to generate suggestions
        ai_suggestions = await ai_service.generate_project_suggestions(
            project_title=project.title,
            project_description=project.description,
            project_location=project.location,
            next_action=project.next_action
        )
        
        # Convert to response format
        suggestions = [SuggestionResponse(**suggestion) for suggestion in ai_suggestions]
        return suggestions
        
    except Exception as e:
        print(f"Error generating AI suggestions: {e}")
        # Return fallback suggestions on error
        return [
            SuggestionResponse(
                title="Review project status",
                description=f"Take 5 minutes to review progress on '{project.title}'",
                estimated_minutes=5,
                energy_level="low",
                context="when feeling stuck",
                reasoning="Reconnecting with your goals provides clarity"
                         )
         ]

@router.get("/ai/health")
async def check_ai_health():
    """Check if Ollama and the AI model are available"""
    is_available = await ai_service.test_connection()
    
    return {
        "ai_available": is_available,
        "model": ai_service.model,
        "base_url": ai_service.base_url
    }

@router.get("/suggestions/quick", response_model=List[SuggestionResponse])
async def get_quick_suggestions(db: Session = Depends(get_db)):
    """Get quick general suggestions when user is idle"""
    
    try:
        # Use AI service to generate quick suggestions
        ai_suggestions = await ai_service.generate_quick_suggestions()
        
        # Convert to response format
        suggestions = [SuggestionResponse(**suggestion) for suggestion in ai_suggestions]
        return suggestions
        
    except Exception as e:
        print(f"Error generating quick AI suggestions: {e}")
        # Return fallback suggestions on error
        return [
            SuggestionResponse(
                title="5-minute declutter",
                description="Clear your immediate workspace of any clutter",
                estimated_minutes=5,
                energy_level="low",
                context="anytime",
                reasoning="A clear space helps clear thinking"
            ),
            SuggestionResponse(
                title="Project check-in",
                description="Review your project list and pick one to focus on",
                estimated_minutes=3,
                energy_level="low",
                context="when feeling lost",
                reasoning="Reconnecting with goals provides direction"
            )
        ] 
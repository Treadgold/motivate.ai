"""
AI Service for generating project suggestions using Ollama
"""

import os
import httpx
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("AI_MODEL", "qwen3max:latest")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))
        
    async def generate_project_suggestions(self, project_title: str, project_description: str = None, 
                                         project_location: str = None, next_action: str = None) -> List[Dict]:
        """Generate AI-powered suggestions for a project"""
        
        # Create context for the AI
        context = f"Project: {project_title}"
        if project_description:
            context += f"\nDescription: {project_description}"
        if project_location:
            context += f"\nLocation: {project_location}"
        if next_action:
            context += f"\nNext planned action: {next_action}"
            
        prompt = f"""You are helping someone manage their personal projects and stay motivated. 

{context}

Generate 3 practical suggestions for 15-minute tasks that would move this project forward. Each suggestion should be:
- Actionable and specific
- Completable in 15 minutes or less
- Motivating and positive
- Appropriate for the energy level described

Please respond with ONLY a JSON array in this exact format:
[
  {{
    "title": "Clear and specific task title",
    "description": "Detailed description of what to do",
    "estimated_minutes": 10,
    "energy_level": "low",
    "context": "when you're feeling overwhelmed",
    "reasoning": "Why this helps with motivation and progress"
  }}
]

Energy levels: "low" (tired, scattered), "medium" (normal), "high" (energetic, focused)
Context examples: "when procrastinating", "when feeling overwhelmed", "when you have energy", "anytime"
"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # Try to parse the JSON response
                    try:
                        # Clean up the response (remove any markdown formatting)
                        clean_response = ai_response.strip()
                        if clean_response.startswith("```json"):
                            clean_response = clean_response[7:]
                        if clean_response.endswith("```"):
                            clean_response = clean_response[:-3]
                        clean_response = clean_response.strip()
                        
                        suggestions = json.loads(clean_response)
                        return suggestions if isinstance(suggestions, list) else []
                        
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI response: {ai_response}")
                        return self._get_fallback_suggestions(project_title, project_location)
                        
                else:
                    print(f"Ollama API error: {response.status_code}")
                    return self._get_fallback_suggestions(project_title, project_location)
                    
        except Exception as e:
            print(f"AI service error: {e}")
            return self._get_fallback_suggestions(project_title, project_location)
    
    async def generate_quick_suggestions(self) -> List[Dict]:
        """Generate quick general suggestions when user is idle"""
        
        prompt = """Generate 2 quick suggestions for someone who is idle and needs motivation to work on their projects. 

Please respond with ONLY a JSON array in this exact format:
[
  {
    "title": "5-minute task title",
    "description": "What to do in detail",
    "estimated_minutes": 5,
    "energy_level": "low",
    "context": "when feeling stuck",
    "reasoning": "Why this helps"
  }
]

Focus on simple, universal tasks that help with motivation and getting unstuck.
"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.8,
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    try:
                        # Clean up the response
                        clean_response = ai_response.strip()
                        if clean_response.startswith("```json"):
                            clean_response = clean_response[7:]
                        if clean_response.endswith("```"):
                            clean_response = clean_response[:-3]
                        clean_response = clean_response.strip()
                        
                        suggestions = json.loads(clean_response)
                        return suggestions if isinstance(suggestions, list) else []
                        
                    except json.JSONDecodeError:
                        return self._get_fallback_quick_suggestions()
                        
                else:
                    return self._get_fallback_quick_suggestions()
                    
        except Exception as e:
            print(f"AI service error: {e}")
            return self._get_fallback_quick_suggestions()
    
    def _get_fallback_suggestions(self, project_title: str, location: str = None) -> List[Dict]:
        """Fallback suggestions when AI is unavailable"""
        location_text = location or "project area"
        
        return [
            {
                "title": "Organize workspace",
                "description": f"Spend 10 minutes tidying up the {location_text}",
                "estimated_minutes": 10,
                "energy_level": "low",
                "context": "when feeling scattered",
                "reasoning": "A clean workspace helps with focus and motivation"
            },
            {
                "title": "Review project status",
                "description": f"Take 5 minutes to think about what's been done on '{project_title}' and what comes next",
                "estimated_minutes": 5,
                "energy_level": "low",
                "context": "when unsure what to do",
                "reasoning": "Clear next steps reduce decision fatigue"
            },
            {
                "title": "Do one small task",
                "description": "Pick the smallest possible step that moves the project forward",
                "estimated_minutes": 15,
                "energy_level": "medium",
                "context": "when procrastinating",
                "reasoning": "Small wins build momentum"
            }
        ]
    
    def _get_fallback_quick_suggestions(self) -> List[Dict]:
        """Fallback quick suggestions when AI is unavailable"""
        return [
            {
                "title": "5-minute declutter",
                "description": "Clear your immediate workspace of any clutter",
                "estimated_minutes": 5,
                "energy_level": "low",
                "context": "anytime",
                "reasoning": "A clear space helps clear thinking"
            },
            {
                "title": "Project check-in",
                "description": "Review your project list and pick one to focus on",
                "estimated_minutes": 3,
                "energy_level": "low",
                "context": "when feeling lost",
                "reasoning": "Reconnecting with goals provides direction"
            }
        ]
    
    async def test_connection(self) -> bool:
        """Test if Ollama is running and the model is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Check if Ollama is running
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    return False
                
                # Check if our model is available
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                return self.model in model_names
                
        except Exception:
            return False 
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import httpx

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.ai_service import AIService

class TestAIService:
    """Test suite for AI service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.ai_service = AIService()
        
    def test_ai_service_initialization(self):
        """Test AI service initializes with correct defaults"""
        assert self.ai_service.base_url == "http://localhost:11434"
        assert self.ai_service.model == "qwen3max:latest"
        assert self.ai_service.timeout == 30
        
    @pytest.mark.asyncio
    async def test_generate_suggestions_success(self):
        """Test successful AI suggestion generation"""
        # Mock the HTTP response
        mock_response = {
            "response": '[{"title": "Test Task", "description": "Test description", "estimated_minutes": 15, "energy_level": "medium", "context": "when focused", "reasoning": "Good for progress"}]'
        }
        
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            
            suggestions = await self.ai_service.generate_project_suggestions(
                "Test Project", 
                "Test description"
            )
            
            assert len(suggestions) == 1
            assert suggestions[0]["title"] == "Test Task"
            assert suggestions[0]["estimated_minutes"] == 15
            
    @pytest.mark.asyncio
    async def test_generate_suggestions_ollama_error(self):
        """Test AI service handles Ollama connection errors gracefully"""
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            
            suggestions = await self.ai_service.generate_project_suggestions("Test Project")
            
            # Should return fallback suggestions
            assert len(suggestions) > 0
            assert all("title" in suggestion for suggestion in suggestions)
            
    @pytest.mark.asyncio
    async def test_generate_suggestions_with_context(self):
        """Test AI suggestion generation with full context"""
        mock_response = {
            "response": '[{"title": "Organize tools", "description": "Sort screwdrivers", "estimated_minutes": 10, "energy_level": "low", "context": "quick win", "reasoning": "Creates visible progress"}]'
        }
        
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            
            suggestions = await self.ai_service.generate_project_suggestions(
                "Garage Organization", 
                "Organize all my tools and equipment",
                "garage",
                "sort through toolbox"
            )
            
            # Verify the service was called with proper context
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "Garage Organization" in call_args[1]["json"]["prompt"]
            assert "garage" in call_args[1]["json"]["prompt"]
            
    def test_health_check(self):
        """Test AI service health check functionality"""
        health_status = self.ai_service.check_health()
        assert "ollama_connected" in health_status
        assert "model_available" in health_status
        assert isinstance(health_status["ollama_connected"], bool) 
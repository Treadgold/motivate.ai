# AI Agent Debugging Guide

## Overview

The AI agent system performs task splitting using a multi-step workflow. This guide helps you debug each step to identify where issues might occur.

## System Architecture

```
Frontend → Backend API → AI Agent Service → Ollama → Response Processing
```

### Key Components

1. **API Endpoints** (`backend/api/ai_agent_api.py`):
   - `POST /api/v1/ai-agent/preview` - Creates operation preview
   - `POST /api/v1/ai-agent/execute/{preview_id}` - Executes approved preview
   - `GET /api/v1/ai-agent/status` - System status

2. **AI Agent Service** (`backend/services/ai_agent_simple.py`):
   - Data gathering (task/project details)
   - AI analysis via Ollama
   - Response parsing and validation
   - Change execution

3. **Ollama Integration**:
   - Model: `qwen3max:latest` (configurable via `AI_MODEL` env var)
   - URL: `http://localhost:11434` (configurable via `OLLAMA_BASE_URL`)
   - Structured JSON prompts for task analysis

## Task Splitting Workflow

### 1. Data Gathering
- Fetches task details from `/api/v1/tasks/{task_id}`
- Fetches project context from `/api/v1/projects/{project_id}`
- Fetches all project tasks for context
- Creates comprehensive context for AI analysis

### 2. AI Analysis
The system sends a structured prompt to Ollama:

```
You are an expert productivity consultant analyzing tasks for optimal splitting.

[Task and Project Context]

Please provide your analysis in this exact JSON format:
{
  "reasoning_steps": [...],
  "task_splits": [{
    "original_task_id": 123,
    "subtasks": [...]
  }],
  "confidence_score": 0.85,
  "impact_assessment": "...",
  "recommendations": [...]
}
```

### 3. Response Processing
- Cleans AI response (removes markdown formatting)
- Parses JSON response
- Converts to internal format (create/delete operations)
- Creates preview for user approval

### 4. Execution (if approved)
- Creates new subtasks via `/api/v1/tasks/bulk`
- Deletes original task via `/api/v1/tasks/{task_id}`

## Common Issues & Debugging

### Issue 1: Ollama Not Responding
**Symptoms**: Connection errors, timeouts
**Debug Steps**:
1. Check if Ollama is running: `ollama list`
2. Check if model is available: `ollama list | grep qwen3max`
3. Test basic request: `curl http://localhost:11434/api/tags`

**Solutions**:
- Start Ollama: `ollama serve`
- Pull model: `ollama pull qwen3max:latest`
- Check firewall/port settings

### Issue 2: Invalid AI Responses
**Symptoms**: JSON parsing errors, malformed responses
**Debug Steps**:
1. Check AI model temperature (should be 0.3 for consistency)
2. Examine raw AI response in logs
3. Test with simpler prompts

**Solutions**:
- Try different model (e.g., `qwen3:14b`)
- Adjust temperature in code
- Add more specific JSON format instructions

### Issue 3: Backend API Errors
**Symptoms**: 404/500 errors when fetching task data
**Debug Steps**:
1. Check if backend is running on port 8010
2. Test task endpoints directly
3. Check database connectivity

**Solutions**:
- Start backend: `cd backend && python main.py`
- Check environment variables
- Verify task IDs exist

### Issue 4: Task Creation Failures
**Symptoms**: Preview works but execution fails
**Debug Steps**:
1. Check task creation endpoint
2. Verify project_id in subtasks
3. Check required task fields

**Solutions**:
- Add missing required fields to subtasks
- Check database constraints
- Verify user permissions

## Debugging Tools

### 1. Comprehensive Debug Script
```bash
cd backend
python debug_ai_agent.py [task_id]
```

This script tests:
- ✅ Ollama connectivity and model availability
- ✅ Simple AI request/response
- ✅ Backend API connectivity  
- ✅ Task data gathering
- ✅ AI prompt creation and response parsing
- ✅ Full agent workflow

### 2. Manual API Testing
```bash
cd backend
python test_ai_agent_manual.py [task_id]
```

This script tests:
- ✅ AI agent status endpoint
- ✅ Supported operations endpoint
- ✅ Task split preview creation
- ✅ Preview details retrieval
- ✅ Preview execution (with confirmation)
- ✅ Preview cancellation

### 3. Quick Status Check
```bash
curl http://localhost:8010/api/v1/ai-agent/status
```

### 4. Direct Ollama Test
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
         "model": "qwen3max:latest",
    "prompt": "Respond with valid JSON: {\"status\": \"working\"}",
    "stream": false
  }'
```

## Environment Configuration

Key environment variables (in `backend/.env`):

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
AI_MODEL=qwen3max:latest
OLLAMA_TIMEOUT=30

# Backend Configuration  
API_BASE_URL=http://127.0.0.1:8010/api/v1

# Database
DATABASE_URL=sqlite:///./motivate.db
```

## Logging and Monitoring

### Enable Debug Logging
Add to your AI agent calls:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor AI Responses
The debug script shows:
- Raw AI responses
- Cleaned responses
- Parsing results
- Error details

### Check Backend Logs
Watch for errors in:
- Task data fetching
- AI service calls
- Response parsing
- Task creation/deletion

## Troubleshooting Checklist

Before debugging, verify:

- [ ] Ollama is running (`ollama serve`)
- [ ] Required model is installed (`ollama pull qwen3max:latest`)
- [ ] Backend is running on port 8010
- [ ] Database is accessible
- [ ] Test task exists with valid project_id
- [ ] Environment variables are set correctly

## Performance Considerations

- **AI Response Time**: 5-30 seconds depending on model and task complexity
- **Timeout Settings**: Default 30 seconds for AI requests
- **Model Size**: Larger models (e.g., 70B) give better results but are slower
- **Temperature**: Lower values (0.1-0.3) give more consistent JSON responses

## Error Recovery

The system includes fallback mechanisms:

1. **AI Unavailable**: Uses rule-based splitting (plan-execute-review pattern)
2. **Parsing Errors**: Falls back to simplified analysis
3. **Network Issues**: Provides clear error messages

## Testing Workflow

1. **Basic Systems**: Run `debug_ai_agent.py` without task ID
2. **Full Workflow**: Run `debug_ai_agent.py <task_id>` with existing task
3. **API Endpoints**: Run `test_ai_agent_manual.py <task_id>`
4. **Production Test**: Use frontend to trigger task splitting

## Getting Help

If issues persist:

1. Check the debug script output for specific failure points
2. Examine raw AI responses for formatting issues
3. Test with different models or simpler tasks
4. Check system resources (CPU/memory for local Ollama)
5. Verify network connectivity between components

The debugging tools provide detailed output to help identify exactly where the issue occurs in the workflow. 
# Motivate.AI API Reference

Complete API documentation for the Motivate.AI backend service.

## Base URL

- **Development**: `http://localhost:8010/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication

Currently, the API does not require authentication. Future versions will implement API key or token-based authentication.

## Common Headers

```http
Content-Type: application/json
Accept: application/json
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": { ... },           // The actual response data
  "message": "Optional success message",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "error_type",
  "message": "Human-readable error description",
  "details": { ... },        // Optional additional details
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Projects API

### List Projects
Get all projects for the user.

```http
GET /projects
```

**Response**: `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "title": "Website Redesign",
      "description": "Complete overhaul of company website",
      "status": "active",
      "priority": "high",
      "estimated_time": 240,
      "actual_time": 120,
      "tags": "web,design,urgent",
      "location": "Office",
      "next_action": "Create wireframes",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "last_worked_on": "2024-01-01T10:30:00Z"
    }
  ]
}
```

### Get Project
Get a specific project by ID.

```http
GET /projects/{project_id}
```

**Parameters**:
- `project_id` (integer) - The project ID

**Response**: `200 OK` (same format as single project above)

**Error Responses**:
- `404 Not Found` - Project doesn't exist

### Create Project
Create a new project.

```http
POST /projects
```

**Request Body**:
```json
{
  "title": "My New Project",           // Required
  "description": "Project description", // Optional
  "priority": "medium",                // Optional: low|medium|high|urgent
  "estimated_time": 480,               // Optional: minutes
  "tags": "web,mobile",                // Optional: comma-separated
  "location": "Home Office",           // Optional
  "next_action": "Setup environment"   // Optional
}
```

**Response**: `201 Created`
```json
{
  "data": {
    "id": 2,
    "title": "My New Project",
    "description": "Project description",
    "status": "active",
    "priority": "medium",
    "estimated_time": 480,
    "actual_time": 0,
    "tags": "web,mobile",
    "location": "Home Office", 
    "next_action": "Setup environment",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "last_worked_on": null
  },
  "message": "Project created successfully"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid data (missing title, etc.)

### Update Project
Update an existing project.

```http
PUT /projects/{project_id}
```

**Parameters**:
- `project_id` (integer) - The project ID

**Request Body** (all fields optional):
```json
{
  "title": "Updated Project Title",
  "description": "Updated description",
  "status": "completed",
  "priority": "high",
  "estimated_time": 600,
  "actual_time": 550,
  "tags": "updated,tags",
  "location": "New Location",
  "next_action": "Deploy to production"
}
```

**Response**: `200 OK` (same format as create)

**Error Responses**:
- `400 Bad Request` - Invalid data
- `404 Not Found` - Project doesn't exist

### Delete Project
Soft delete a project (sets is_active to false).

```http
DELETE /projects/{project_id}
```

**Parameters**:
- `project_id` (integer) - The project ID

**Response**: `200 OK`
```json
{
  "message": "Project deleted successfully"
}
```

**Error Responses**:
- `404 Not Found` - Project doesn't exist

---

## Tasks API

### List Tasks
Get all tasks, optionally filtered by project.

```http
GET /tasks?project_id={project_id}
```

**Query Parameters**:
- `project_id` (integer, optional) - Filter tasks by project

**Response**: `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "title": "Setup development environment",
      "description": "Install dependencies and configure tools",
      "status": "pending",
      "priority": "medium",
      "estimated_minutes": 30,
      "actual_minutes": 0,
      "is_suggestion": false,
      "energy_level": "medium",
      "context": "when focused and interruption-free",
      "is_completed": false,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "completed_at": null
    }
  ]
}
```

### Get Task
Get a specific task by ID.

```http
GET /tasks/{task_id}
```

**Parameters**:
- `task_id` (integer) - The task ID

**Response**: `200 OK` (same format as single task above)

**Error Responses**:
- `404 Not Found` - Task doesn't exist

### Create Task
Create a new task.

```http
POST /tasks
```

**Request Body**:
```json
{
  "project_id": 1,                    // Required
  "title": "Implement user login",    // Required
  "description": "Create login form and authentication", // Optional
  "status": "pending",                // Optional: pending|in_progress|completed
  "priority": "medium",               // Optional: low|medium|high|urgent
  "estimated_minutes": 45,            // Optional: default 15
  "energy_level": "medium",           // Optional: low|medium|high
  "context": "when you have focus time", // Optional
  "is_suggestion": false              // Optional: default false
}
```

**Response**: `201 Created`
```json
{
  "data": {
    "id": 2,
    "project_id": 1,
    "title": "Implement user login",
    "description": "Create login form and authentication",
    "status": "pending",
    "priority": "medium",
    "estimated_minutes": 45,
    "actual_minutes": 0,
    "is_suggestion": false,
    "energy_level": "medium",
    "context": "when you have focus time",
    "is_completed": false,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "completed_at": null
  },
  "message": "Task created successfully"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid data (missing required fields)
- `404 Not Found` - Project doesn't exist

### Update Task
Update an existing task.

```http
PUT /tasks/{task_id}
```

**Parameters**:
- `task_id` (integer) - The task ID

**Request Body** (all fields optional):
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "high",
  "estimated_minutes": 60,
  "actual_minutes": 30,
  "energy_level": "high",
  "context": "when energized",
  "is_completed": true
}
```

**Response**: `200 OK` (same format as create)

**Error Responses**:
- `400 Bad Request` - Invalid data
- `404 Not Found` - Task doesn't exist

### Complete Task
Mark a task as completed (convenience endpoint).

```http
PUT /tasks/{task_id}/complete
```

**Parameters**:
- `task_id` (integer) - The task ID

**Response**: `200 OK`
```json
{
  "message": "Task completed successfully"
}
```

**Error Responses**:
- `404 Not Found` - Task doesn't exist

### Delete Task
Delete a task permanently.

```http
DELETE /tasks/{task_id}
```

**Parameters**:
- `task_id` (integer) - The task ID

**Response**: `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses**:
- `404 Not Found` - Task doesn't exist

### Bulk Create Tasks
Create multiple tasks at once.

```http
POST /tasks/bulk
```

**Request Body**:
```json
{
  "tasks": [
    {
      "project_id": 1,
      "title": "Task 1",
      "description": "First task",
      "estimated_minutes": 15
    },
    {
      "project_id": 1,
      "title": "Task 2", 
      "description": "Second task",
      "estimated_minutes": 30
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "data": [
    // Array of created tasks (same format as single task)
  ],
  "message": "Tasks created successfully"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid task data

---

## AI Agent API

### Preview Task Split
Generate a preview of how AI would split a complex task.

```http
POST /ai-agent/preview
```

**Request Body**:
```json
{
  "task_id": 1,
  "split_preferences": {
    "max_subtask_minutes": 20,
    "energy_level": "medium"
  }
}
```

**Response**: `200 OK`
```json
{
  "data": {
    "preview_id": "uuid-string",
    "original_task": {
      // Task object
    },
    "suggested_subtasks": [
      {
        "title": "Research authentication libraries",
        "description": "Compare different auth solutions",
        "estimated_minutes": 15,
        "energy_level": "medium",
        "context": "when you need to focus"
      }
    ],
    "ai_reasoning": "This task is complex and can be broken down into smaller, focused pieces...",
    "confidence_score": 85
  }
}
```

**Error Responses**:
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Task doesn't exist
- `503 Service Unavailable` - AI service unavailable

### Execute Task Split
Execute a previously previewed task split.

```http
POST /ai-agent/execute/{preview_id}
```

**Parameters**:
- `preview_id` (string) - UUID from preview request

**Response**: `200 OK`
```json
{
  "data": {
    "original_task_id": 1,
    "created_subtasks": [
      // Array of created subtask objects
    ]
  },
  "message": "Task split executed successfully"
}
```

**Error Responses**:
- `404 Not Found` - Preview not found or expired
- `400 Bad Request` - Preview already executed

### Get AI Agent Status
Check the status of the AI agent service.

```http
GET /ai-agent/status
```

**Response**: `200 OK`
```json
{
  "data": {
    "status": "online",         // online|degraded|offline
    "model_available": true,
    "last_health_check": "2024-01-01T12:00:00Z",
    "capabilities": [
      "task_splitting",
      "suggestions"
    ]
  }
}
```

### Cancel Preview
Cancel a task split preview.

```http
DELETE /ai-agent/preview/{preview_id}
```

**Parameters**:
- `preview_id` (string) - UUID from preview request

**Response**: `200 OK`
```json
{
  "message": "Preview cancelled successfully"
}
```

---

## Suggestions API

### Get Contextual Suggestions
Get AI-powered suggestions based on current context.

```http
GET /suggestions/contextual?energy_level={level}&available_time={minutes}
```

**Query Parameters**:
- `energy_level` (string, optional) - low|medium|high
- `available_time` (integer, optional) - Minutes available

**Response**: `200 OK`
```json
{
  "data": {
    "suggestions": [
      {
        "task_id": 1,
        "reason": "Good match for your current energy level",
        "confidence": 90
      }
    ],
    "context": {
      "energy_level": "medium",
      "available_time": 30
    }
  }
}
```

### Get Next Suggestion
Get the next recommended task to work on.

```http
GET /suggestions/next
```

**Response**: `200 OK`
```json
{
  "data": {
    "task": {
      // Complete task object
    },
    "reason": "This task matches your current context and energy",
    "confidence": 85
  }
}
```

---

## Activity API

### Log Activity
Log user activity for analytics and suggestions.

```http
POST /activity
```

**Request Body**:
```json
{
  "task_id": 1,              // Optional
  "activity_type": "work",   // work|break|idle
  "duration_minutes": 25,
  "notes": "Completed login implementation"
}
```

**Response**: `201 Created`
```json
{
  "data": {
    "id": 1,
    "task_id": 1,
    "activity_type": "work",
    "duration_minutes": 25,
    "notes": "Completed login implementation",
    "logged_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get Today's Progress
Get progress summary for today.

```http
GET /progress/today
```

**Response**: `200 OK`
```json
{
  "data": {
    "total_minutes": 120,
    "tasks_completed": 3,
    "projects_worked_on": 2,
    "energy_trends": {
      "morning": "high",
      "afternoon": "medium",
      "evening": "low"
    }
  }
}
```

---

## System Endpoints

### Health Check
Check API health status.

```http
GET /health
```

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "ai_service": "available"
}
```

### API Documentation
Interactive API documentation (Swagger UI).

```http
GET /docs
```

**Response**: HTML page with interactive API documentation

---

## Error Codes

### HTTP Status Codes
- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST  
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Client error (validation, malformed request)
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Custom Error Types
- `validation_error` - Input validation failed
- `resource_not_found` - Requested resource doesn't exist
- `database_error` - Database operation failed
- `ai_service_error` - AI service unavailable or failed
- `rate_limit_exceeded` - Too many requests
- `internal_error` - Unexpected server error

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions will implement:
- 1000 requests per hour per client
- 100 AI requests per hour per client
- Burst allowance of 50 requests per minute

---

## SDK Examples

### Python (requests)
```python
import requests

# Base configuration
API_BASE = "http://localhost:8010/api/v1"
headers = {"Content-Type": "application/json"}

# Create a project
project_data = {
    "title": "My Project",
    "description": "A sample project",
    "priority": "medium"
}
response = requests.post(f"{API_BASE}/projects", 
                        json=project_data, headers=headers)
project = response.json()["data"]

# Create a task
task_data = {
    "project_id": project["id"],
    "title": "Sample task",
    "estimated_minutes": 30
}
response = requests.post(f"{API_BASE}/tasks", 
                        json=task_data, headers=headers)
task = response.json()["data"]

# Complete the task
response = requests.put(f"{API_BASE}/tasks/{task['id']}/complete")
```

### JavaScript (fetch)
```javascript
const API_BASE = "http://localhost:8010/api/v1";

// Create a project
const projectData = {
  title: "My Project",
  description: "A sample project",
  priority: "medium"
};

const response = await fetch(`${API_BASE}/projects`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify(projectData)
});

const project = await response.json();
```

---

## Changelog

### v1.0.0 (Current)
- ✅ Complete Projects CRUD API
- ✅ Complete Tasks CRUD API  
- ✅ AI Agent task splitting
- ✅ Contextual suggestions
- ✅ Activity logging
- ✅ Health checks and status

### Future Versions
- 🔜 Authentication and user management
- 🔜 Rate limiting
- 🔜 WebSocket support for real-time updates
- 🔜 File upload for task attachments
- 🔜 Advanced analytics and reporting

---

*For development setup and architecture details, see [Getting Started Guide](GETTING_STARTED.md) and [Project Structure](PROJECT_STRUCTURE.md).*
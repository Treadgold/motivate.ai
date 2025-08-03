# Database Schema Documentation

This document describes the database schema for Motivate.AI, including all tables, relationships, and data types.

## Overview

Motivate.AI uses SQLite for development and PostgreSQL for production. The ORM is SQLAlchemy with Alembic for migrations.

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Projects   │   1:N │    Tasks    │   1:N │  Activity   │
│             │◄──────│             │◄──────│             │
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ title       │       │ project_id  │       │ task_id     │
│ description │       │ title       │       │ duration    │
│ status      │       │ description │       │ activity_   │
│ priority    │       │ status      │       │   type      │
│ ...         │       │ priority    │       │ ...         │
└─────────────┘       │ ...         │       └─────────────┘
                      └─────────────┘
```

---

## Tables

### 1. Projects Table

Stores project information and metadata.

**Table Name**: `projects`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique project identifier |
| `title` | VARCHAR(255) | NOT NULL, INDEX | Project title/name |
| `description` | TEXT | NULLABLE | Detailed project description |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'active' | Project status |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Project priority level |
| `estimated_time` | INTEGER | NULLABLE | Estimated total time in minutes |
| `actual_time` | INTEGER | DEFAULT 0 | Actual time spent in minutes |
| `tags` | VARCHAR(500) | NULLABLE | Comma-separated tags |
| `location` | VARCHAR(255) | NULLABLE | Where project work happens |
| `next_action` | VARCHAR(500) | NULLABLE | Next action to take |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete flag |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `last_worked_on` | TIMESTAMP | NULLABLE | Last activity timestamp |

**Indexes**:
- `ix_projects_title` on `title`
- `ix_projects_status` on `status`
- `ix_projects_priority` on `priority`

**Valid Values**:
- `status`: 'active', 'completed', 'paused', 'cancelled'
- `priority`: 'low', 'medium', 'high', 'urgent'

**Example Data**:
```json
{
  "id": 1,
  "title": "Website Redesign",
  "description": "Complete overhaul of company website with modern design",
  "status": "active",
  "priority": "high",
  "estimated_time": 2400,
  "actual_time": 480,
  "tags": "web,design,urgent",
  "location": "Office",
  "next_action": "Create wireframes for homepage",
  "is_active": true,
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-02T14:30:00Z",
  "last_worked_on": "2024-01-02T14:30:00Z"
}
```

---

### 2. Tasks Table

Stores individual tasks within projects.

**Table Name**: `tasks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| `project_id` | INTEGER | NOT NULL, FOREIGN KEY | Reference to projects.id |
| `title` | VARCHAR(255) | NOT NULL, INDEX | Task title/name |
| `description` | TEXT | NULLABLE | Detailed task description |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'pending' | Task status |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Task priority level |
| `estimated_minutes` | INTEGER | NOT NULL, DEFAULT 15 | Estimated time in minutes |
| `actual_minutes` | INTEGER | DEFAULT 0 | Actual time spent in minutes |
| `is_suggestion` | BOOLEAN | NOT NULL, DEFAULT FALSE | AI-generated suggestion flag |
| `energy_level` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Required energy level |
| `context` | VARCHAR(500) | NULLABLE | When/where to do this task |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NULLABLE | Last update timestamp |
| `completed_at` | TIMESTAMP | NULLABLE | Completion timestamp |

**Foreign Keys**:
- `project_id` → `projects.id` (CASCADE DELETE)

**Indexes**:
- `ix_tasks_project_id` on `project_id`
- `ix_tasks_title` on `title`
- `ix_tasks_status` on `status`
- `ix_tasks_priority` on `priority`
- `ix_tasks_is_completed` on `is_completed`

**Valid Values**:
- `status`: 'pending', 'in_progress', 'completed', 'blocked', 'cancelled'
- `priority`: 'low', 'medium', 'high', 'urgent'
- `energy_level`: 'low', 'medium', 'high'

**Example Data**:
```json
{
  "id": 1,
  "project_id": 1,
  "title": "Create homepage wireframes",
  "description": "Design wireframes for the new homepage layout including navigation, hero section, and footer",
  "status": "in_progress",
  "priority": "high",
  "estimated_minutes": 60,
  "actual_minutes": 45,
  "is_suggestion": false,
  "energy_level": "high",
  "context": "when you have uninterrupted focus time",
  "is_completed": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:30:00Z",
  "completed_at": null
}
```

---

### 3. Activity Table

Stores activity logs for analytics and time tracking.

**Table Name**: `activity`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique activity identifier |
| `task_id` | INTEGER | NULLABLE, FOREIGN KEY | Reference to tasks.id |
| `project_id` | INTEGER | NULLABLE, FOREIGN KEY | Reference to projects.id |
| `activity_type` | VARCHAR(50) | NOT NULL | Type of activity |
| `duration_minutes` | INTEGER | NOT NULL | Duration in minutes |
| `notes` | TEXT | NULLABLE | Optional activity notes |
| `energy_level` | VARCHAR(20) | NULLABLE | User's energy during activity |
| `context` | VARCHAR(500) | NULLABLE | Context/environment info |
| `logged_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When activity was logged |
| `started_at` | TIMESTAMP | NULLABLE | When activity actually started |
| `ended_at` | TIMESTAMP | NULLABLE | When activity actually ended |

**Foreign Keys**:
- `task_id` → `tasks.id` (SET NULL on delete)
- `project_id` → `projects.id` (SET NULL on delete)

**Indexes**:
- `ix_activity_task_id` on `task_id`
- `ix_activity_project_id` on `project_id`
- `ix_activity_logged_at` on `logged_at`
- `ix_activity_type` on `activity_type`

**Valid Values**:
- `activity_type`: 'work', 'break', 'planning', 'review', 'research', 'meeting', 'idle'
- `energy_level`: 'low', 'medium', 'high'

**Example Data**:
```json
{
  "id": 1,
  "task_id": 1,
  "project_id": 1,
  "activity_type": "work",
  "duration_minutes": 45,
  "notes": "Made good progress on wireframes, completed navigation section",
  "energy_level": "high",
  "context": "quiet office environment",
  "logged_at": "2024-01-01T11:30:00Z",
  "started_at": "2024-01-01T10:45:00Z",
  "ended_at": "2024-01-01T11:30:00Z"
}
```

---

## Relationships

### 1. Projects → Tasks (One-to-Many)
- One project can have many tasks
- Each task belongs to exactly one project
- When a project is deleted, all its tasks are also deleted (CASCADE)

```sql
-- Get all tasks for a project
SELECT * FROM tasks WHERE project_id = 1;

-- Get project with its tasks (JOIN)
SELECT p.*, t.id as task_id, t.title as task_title
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
WHERE p.id = 1;
```

### 2. Tasks → Activity (One-to-Many)
- One task can have many activity logs
- Each activity log can be associated with one task (optional)
- When a task is deleted, associated activities remain but task_id is set to NULL

```sql
-- Get all activity for a task
SELECT * FROM activity WHERE task_id = 1;

-- Get task with its activity logs
SELECT t.*, a.duration_minutes, a.logged_at
FROM tasks t
LEFT JOIN activity a ON t.id = a.task_id
WHERE t.id = 1;
```

### 3. Projects → Activity (One-to-Many)
- One project can have many activity logs
- Activity can be logged at project level (not task-specific)
- When a project is deleted, associated activities remain but project_id is set to NULL

```sql
-- Get all activity for a project (direct + task-related)
SELECT * FROM activity 
WHERE project_id = 1 OR task_id IN (
    SELECT id FROM tasks WHERE project_id = 1
);
```

---

## Database Constraints

### Referential Integrity
```sql
-- Foreign key constraints
ALTER TABLE tasks 
ADD CONSTRAINT fk_tasks_project_id 
FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;

ALTER TABLE activity 
ADD CONSTRAINT fk_activity_task_id 
FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL;

ALTER TABLE activity 
ADD CONSTRAINT fk_activity_project_id 
FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL;
```

### Check Constraints
```sql
-- Priority values
ALTER TABLE projects 
ADD CONSTRAINT check_project_priority 
CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

ALTER TABLE tasks 
ADD CONSTRAINT check_task_priority 
CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

-- Status values
ALTER TABLE projects 
ADD CONSTRAINT check_project_status 
CHECK (status IN ('active', 'completed', 'paused', 'cancelled'));

ALTER TABLE tasks 
ADD CONSTRAINT check_task_status 
CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled'));

-- Energy levels
ALTER TABLE tasks 
ADD CONSTRAINT check_task_energy_level 
CHECK (energy_level IN ('low', 'medium', 'high'));

-- Time constraints
ALTER TABLE projects 
ADD CONSTRAINT check_project_time_positive 
CHECK (estimated_time >= 0 AND actual_time >= 0);

ALTER TABLE tasks 
ADD CONSTRAINT check_task_time_positive 
CHECK (estimated_minutes > 0 AND actual_minutes >= 0);

ALTER TABLE activity 
ADD CONSTRAINT check_activity_duration_positive 
CHECK (duration_minutes > 0);
```

---

## Sample Queries

### Common Project Queries

```sql
-- Get active projects with task counts
SELECT p.*, COUNT(t.id) as task_count
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id AND t.is_completed = FALSE
WHERE p.is_active = TRUE
GROUP BY p.id
ORDER BY p.priority DESC, p.updated_at DESC;

-- Get projects with completion percentage
SELECT p.*,
       COUNT(t.id) as total_tasks,
       COUNT(CASE WHEN t.is_completed THEN 1 END) as completed_tasks,
       ROUND(COUNT(CASE WHEN t.is_completed THEN 1 END) * 100.0 / COUNT(t.id), 2) as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
WHERE p.is_active = TRUE
GROUP BY p.id;

-- Get recently active projects
SELECT DISTINCT p.*
FROM projects p
JOIN activity a ON p.id = a.project_id
WHERE a.logged_at >= datetime('now', '-7 days')
ORDER BY a.logged_at DESC;
```

### Common Task Queries

```sql
-- Get tasks ready to work on (pending, with context)
SELECT t.*, p.title as project_title
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.status = 'pending' 
  AND t.is_completed = FALSE
  AND p.is_active = TRUE
ORDER BY t.priority DESC, t.estimated_minutes ASC;

-- Get overdue or long-running tasks
SELECT t.*, p.title as project_title,
       datetime('now') - t.created_at as days_old
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.status = 'in_progress' 
  AND t.updated_at < datetime('now', '-3 days')
ORDER BY t.updated_at ASC;

-- Get AI suggestions
SELECT t.*, p.title as project_title
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.is_suggestion = TRUE
  AND t.is_completed = FALSE
ORDER BY t.created_at DESC;
```

### Analytics Queries

```sql
-- Daily productivity summary
SELECT date(a.logged_at) as work_date,
       SUM(a.duration_minutes) as total_minutes,
       COUNT(DISTINCT a.task_id) as tasks_worked_on,
       COUNT(DISTINCT a.project_id) as projects_touched
FROM activity a
WHERE a.activity_type = 'work'
  AND a.logged_at >= datetime('now', '-30 days')
GROUP BY date(a.logged_at)
ORDER BY work_date DESC;

-- Project time tracking
SELECT p.title,
       SUM(a.duration_minutes) as total_time_logged,
       COUNT(t.id) as total_tasks,
       COUNT(CASE WHEN t.is_completed THEN 1 END) as completed_tasks
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN activity a ON t.id = a.task_id AND a.activity_type = 'work'
WHERE p.is_active = TRUE
GROUP BY p.id, p.title
ORDER BY total_time_logged DESC;

-- Energy level analysis
SELECT a.energy_level,
       AVG(a.duration_minutes) as avg_session_length,
       SUM(a.duration_minutes) as total_time,
       COUNT(*) as session_count
FROM activity a
WHERE a.activity_type = 'work'
  AND a.energy_level IS NOT NULL
  AND a.logged_at >= datetime('now', '-30 days')
GROUP BY a.energy_level;
```

---

## Database Maintenance

### Regular Cleanup Operations

```sql
-- Archive old completed tasks (older than 90 days)
UPDATE tasks 
SET is_completed = TRUE, status = 'archived'
WHERE is_completed = TRUE 
  AND completed_at < datetime('now', '-90 days');

-- Clean up orphaned activity logs (optional)
DELETE FROM activity 
WHERE task_id IS NULL 
  AND project_id IS NULL 
  AND logged_at < datetime('now', '-365 days');

-- Update project last_worked_on timestamps
UPDATE projects 
SET last_worked_on = (
    SELECT MAX(a.logged_at)
    FROM activity a
    WHERE a.project_id = projects.id
       OR a.task_id IN (
           SELECT id FROM tasks WHERE project_id = projects.id
       )
);
```

### Performance Optimization

```sql
-- Analyze table statistics
ANALYZE projects;
ANALYZE tasks;
ANALYZE activity;

-- Vacuum database (SQLite)
VACUUM;

-- Reindex for better performance
REINDEX ix_tasks_project_id;
REINDEX ix_activity_logged_at;
```

---

## Migration History

### Version 1.0.0 (Initial Schema)
- Created `projects` table with basic fields
- Created `tasks` table with project relationship
- Added basic indexes

### Version 1.1.0 (Activity Tracking)
- Added `activity` table for time tracking
- Added foreign key relationships
- Added energy_level and context fields

### Version 1.2.0 (AI Features)
- Added `is_suggestion` field to tasks
- Added `energy_level` to tasks
- Enhanced context fields

### Planned Migrations
- **v1.3.0**: Add user authentication tables
- **v1.4.0**: Add task templates table
- **v1.5.0**: Add file attachments support

---

## Data Types by Database

### SQLite (Development)
- `INTEGER` → SQLite INTEGER
- `VARCHAR(n)` → SQLite TEXT
- `TEXT` → SQLite TEXT
- `BOOLEAN` → SQLite INTEGER (0/1)
- `TIMESTAMP` → SQLite TEXT (ISO8601)

### PostgreSQL (Production)
- `INTEGER` → PostgreSQL INTEGER
- `VARCHAR(n)` → PostgreSQL VARCHAR(n)
- `TEXT` → PostgreSQL TEXT
- `BOOLEAN` → PostgreSQL BOOLEAN
- `TIMESTAMP` → PostgreSQL TIMESTAMP WITH TIME ZONE

---

## Backup and Recovery

### Development (SQLite)
```bash
# Backup database
cp motivate_ai.db motivate_ai_backup_$(date +%Y%m%d).db

# Restore database
cp motivate_ai_backup_20240101.db motivate_ai.db
```

### Production (PostgreSQL)
```bash
# Backup database
pg_dump motivate_ai_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql motivate_ai_prod < backup_20240101_120000.sql
```

---

*This schema has been designed for scalability and performance while maintaining data integrity and supporting the core features of Motivate.AI.*
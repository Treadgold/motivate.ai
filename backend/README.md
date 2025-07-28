# Backend - FastAPI Server

The backend API server for the Motivate.AI project companion.

## 🚀 Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🏃 Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

API will be available at: http://localhost:8010
API docs at: http://localhost:8010/docs

## 📁 Structure

```
backend/
├── main.py              # FastAPI app entry point
├── models/              # Database models
├── api/                 # API routes
├── services/            # Business logic
├── database.py          # Database setup
└── requirements.txt     # Python dependencies
```

## 🔗 API Endpoints

- `/projects` - Manage projects
- `/tasks` - Manage tasks
- `/suggestions` - AI-generated suggestions
- `/activity` - Activity logging 
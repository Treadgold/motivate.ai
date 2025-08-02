from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os

# Load environment variables
load_dotenv()

# Import database setup
from database import create_tables, get_db

app = FastAPI(
    title="Motivate.AI API",
    description="AI-guided project companion backend",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api import projects, tasks, suggestions, activity, ai_agent_api

# Include API routes
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(suggestions.router, prefix="/api/v1")
app.include_router(activity.router, prefix="/api/v1")
app.include_router(ai_agent_api.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Motivate.AI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-simple")
async def test_simple():
    """Simple endpoint with no dependencies"""
    return {"message": "Simple test", "timestamp": "2024-01-01"}

@app.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test endpoint with database dependency"""
    return {"message": "DB test", "count": 42}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010) 
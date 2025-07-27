from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # active, paused, completed, abandoned
    priority = Column(String(20), default="medium")  # low, medium, high
    estimated_time = Column(Integer)  # estimated total time in minutes
    actual_time = Column(Integer, default=0)  # actual time spent in minutes
    tags = Column(String(500))  # comma-separated tags
    location = Column(String(200))  # where the project is physically
    next_action = Column(Text)  # what's the next small step
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_worked_on = Column(DateTime(timezone=True))
    
    # Relationship to tasks
    tasks = relationship("Task", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', status='{self.status}')>" 
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    activity_type = Column(String(50), nullable=False)  # work_session, note, break, completion
    description = Column(Text)
    duration_minutes = Column(Integer)  # how long this activity lasted
    mood = Column(String(20))  # user's mood: energetic, tired, focused, scattered, etc.
    productivity_rating = Column(Integer)  # 1-5 scale
    notes = Column(Text)  # any additional notes
    source = Column(String(50), default="manual")  # manual, desktop_app, mobile_app, auto
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Activity(id={self.id}, type='{self.activity_type}', duration={self.duration_minutes})>" 
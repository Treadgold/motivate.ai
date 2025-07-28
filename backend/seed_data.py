#!/usr/bin/env python3
"""
Seed Data Script for Motivate.AI

This script clears existing data and populates the database with realistic test data.
Run this script only when you need fresh test data.

Usage: python seed_data.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import os

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.project import Project
from models.task import Task

def clear_database():
    """Clear all existing data from the database."""
    print("🗑️  Clearing existing data...")
    
    db = SessionLocal()
    try:
        # Delete all tasks first (due to foreign key constraints)
        deleted_tasks = db.query(Task).delete()
        print(f"   Deleted {deleted_tasks} tasks")
        
        # Delete all projects
        deleted_projects = db.query(Project).delete()
        print(f"   Deleted {deleted_projects} projects")
        
        db.commit()
        print("✅ Database cleared successfully")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_projects():
    """Create realistic test projects with associated tasks."""
    print("📋 Creating test projects and tasks...")
    
    db = SessionLocal()
    try:
        # Project 1: Home Office Setup
        project1 = Project(
            title="Home Office Productivity Upgrade",
            description="Transform my workspace into a productive and inspiring environment for focused work.",
            status="active",
            priority="high",
            estimated_time=480,  # 8 hours
            actual_time=120,     # 2 hours done
            tags="workspace,productivity,ergonomics,focus",
            location="Home office/guest room",
            next_action="Research and order ergonomic chair",
            last_worked_on=datetime.now() - timedelta(days=2)
        )
        db.add(project1)
        db.flush()  # Get the ID for tasks
        
        # Tasks for Project 1
        project1_tasks = [
            Task(
                project_id=project1.id,
                title="Research ergonomic office chairs",
                description="Find a chair that supports good posture for long work sessions under $400",
                status="in_progress",
                priority="high",
                estimated_minutes=60,
                actual_minutes=30,
                energy_level="medium",
                context="When I need a break from deep work"
            ),
            Task(
                project_id=project1.id,
                title="Set up proper lighting",
                description="Install LED desk lamp and adjust room lighting to reduce eye strain",
                status="pending",
                priority="medium",
                estimated_minutes=45,
                energy_level="low",
                context="Weekend afternoon project"
            ),
            Task(
                project_id=project1.id,
                title="Organize desk cables",
                description="Use cable management solutions to clean up the messy cables under desk",
                status="pending",
                priority="low",
                estimated_minutes=30,
                energy_level="low",
                context="Quick organizing session"
            ),
            Task(
                project_id=project1.id,
                title="Create daily shutdown ritual",
                description="Design a 10-minute routine to properly close work and prepare for tomorrow",
                status="pending",
                priority="medium",
                estimated_minutes=20,
                energy_level="medium",
                context="End of workday reflection time"
            )
        ]
        
        # Project 2: Learning Project
        project2 = Project(
            title="Learn Spanish for Travel",
            description="Build conversational Spanish skills for upcoming trip to Barcelona and general life enrichment.",
            status="active",
            priority="medium",
            estimated_time=600,  # 10 hours
            actual_time=45,      # Just started
            tags="language,travel,personal-growth,culture",
            location="Various - phone app, books, online",
            next_action="Complete Duolingo lesson and practice pronunciation",
            last_worked_on=datetime.now() - timedelta(days=1)
        )
        db.add(project2)
        db.flush()
        
        # Tasks for Project 2
        project2_tasks = [
            Task(
                project_id=project2.id,
                title="Complete 20 minutes of Duolingo daily",
                description="Work through lessons focusing on travel vocabulary and basic conversations",
                status="in_progress",
                priority="high",
                estimated_minutes=20,
                actual_minutes=15,
                energy_level="low",
                context="Morning routine or commute time"
            ),
            Task(
                project_id=project2.id,
                title="Watch Spanish Netflix show with subtitles",
                description="Start with English subtitles, gradually switch to Spanish subtitles",
                status="pending",
                priority="low",
                estimated_minutes=45,
                energy_level="low",
                context="Evening relaxation time"
            ),
            Task(
                project_id=project2.id,
                title="Practice ordering food in Spanish",
                description="Learn restaurant vocabulary and practice common phrases for dining out",
                status="pending",
                priority="medium",
                estimated_minutes=30,
                energy_level="medium",
                context="Before meals, when thinking about food"
            ),
            Task(
                project_id=project2.id,
                title="Join online Spanish conversation group",
                description="Find and participate in a weekly Spanish practice group to build confidence",
                status="pending",
                priority="medium",
                estimated_minutes=60,
                energy_level="high",
                context="When feeling social and energetic"
            )
        ]
        
        # Project 3: Health & Fitness
        project3 = Project(
            title="Morning Energy & Fitness Routine",
            description="Establish a sustainable morning routine that boosts energy and builds strength without feeling overwhelming.",
            status="active",
            priority="high",
            estimated_time=300,  # 5 hours to establish
            actual_time=90,      # 1.5 hours in
            tags="health,fitness,routine,energy,morning",
            location="Home and local gym",
            next_action="Do 20-minute bodyweight workout",
            last_worked_on=datetime.now()  # Worked on today
        )
        db.add(project3)
        db.flush()
        
        # Tasks for Project 3
        project3_tasks = [
            Task(
                project_id=project3.id,
                title="20-minute bodyweight workout",
                description="Pushups, squats, planks - simple routine that doesn't require equipment",
                status="completed",
                priority="high",
                estimated_minutes=20,
                actual_minutes=25,
                energy_level="high",
                context="Right after waking up",
                is_completed=True,
                completed_at=datetime.now() - timedelta(hours=2)
            ),
            Task(
                project_id=project3.id,
                title="Meal prep healthy breakfast options",
                description="Prepare overnight oats and cut fruit for easy grab-and-go mornings",
                status="pending",
                priority="medium",
                estimated_minutes=45,
                energy_level="medium",
                context="Sunday afternoon prep time"
            ),
            Task(
                project_id=project3.id,
                title="Set consistent wake-up time",
                description="Choose a wake-up time and stick to it for 7 days straight, including weekends",
                status="in_progress",
                priority="high",
                estimated_minutes=5,
                energy_level="medium",
                context="Every evening when setting alarm"
            ),
            Task(
                project_id=project3.id,
                title="Try 10-minute meditation",
                description="Use app or guided meditation to start the day with mental clarity",
                status="pending",
                priority="low",
                estimated_minutes=10,
                energy_level="low",
                context="After workout, before shower"
            )
        ]
        
        # Project 4: Creative Project
        project4 = Project(
            title="Start Photography Side Project",
            description="Develop photography skills and build a portfolio of local urban architecture and street scenes.",
            status="active",
            priority="low",
            estimated_time=720,  # 12 hours
            actual_time=0,       # Haven't started yet
            tags="photography,creative,portfolio,art,urban",
            location="Around the city, various neighborhoods",
            next_action="Research basic photography composition rules",
            last_worked_on=None  # Haven't started
        )
        db.add(project4)
        db.flush()
        
        # Tasks for Project 4
        project4_tasks = [
            Task(
                project_id=project4.id,
                title="Learn rule of thirds and basic composition",
                description="Watch YouTube tutorials and practice with phone camera first",
                status="pending",
                priority="high",
                estimated_minutes=60,
                energy_level="medium",
                context="When I want to learn something new"
            ),
            Task(
                project_id=project4.id,
                title="Take 50 practice photos downtown",
                description="Focus on buildings, interesting angles, and street scenes",
                status="pending",
                priority="medium",
                estimated_minutes=120,
                energy_level="high",
                context="Weekend afternoon when weather is nice"
            ),
            Task(
                project_id=project4.id,
                title="Research local photography groups",
                description="Find meetups or online communities for feedback and inspiration",
                status="pending",
                priority="low",
                estimated_minutes=30,
                energy_level="low",
                context="Evening browsing time"
            ),
            Task(
                project_id=project4.id,
                title="Set up Instagram account for portfolio",
                description="Create dedicated account to share best photos and connect with other photographers",
                status="pending",
                priority="low",
                estimated_minutes=25,
                energy_level="low",
                context="When I have a few good photos to share"
            )
        ]
        
        # Add all tasks to the session
        for task_list in [project1_tasks, project2_tasks, project3_tasks, project4_tasks]:
            for task in task_list:
                db.add(task)
        
        # Commit all changes
        db.commit()
        
        print("✅ Created 4 projects with associated tasks:")
        print(f"   📋 {project1.title} (4 tasks)")
        print(f"   📋 {project2.title} (4 tasks)")
        print(f"   📋 {project3.title} (4 tasks)")
        print(f"   📋 {project4.title} (4 tasks)")
        print("   Total: 16 tasks across various priorities and contexts")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to seed the database with test data."""
    print("🌱 Motivate.AI Database Seeding")
    print("=" * 40)
    
    # Ask for confirmation before clearing data
    response = input("This will DELETE all existing data and replace it with test data. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Seeding cancelled.")
        return
    
    try:
        clear_database()
        create_test_projects()
        print("\n🎉 Database seeding completed successfully!")
        print("\nTest data includes:")
        print("• Projects with realistic goals and contexts")
        print("• Tasks at different completion stages")
        print("• Various priority levels and energy requirements")
        print("• Time estimates and tracking")
        print("• Contextual information for when to work on tasks")
        
    except Exception as e:
        print(f"\n💥 Seeding failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
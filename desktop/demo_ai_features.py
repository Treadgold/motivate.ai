"""
Motivate.AI - AI Features Demo

This script demonstrates the new AI task splitting capabilities.
Run this after starting the backend to see the AI assistant in action!
"""

import requests
import json
from typing import Dict, List

def demo_ai_features():
    """Demonstrate the AI features"""
    api_base_url = "http://127.0.0.1:8010/api/v1"
    
    print("🤖 Motivate.AI - AI Task Splitting Demo")
    print("=" * 50)
    
    # Check AI status
    print("\n1. Checking AI Agent Status...")
    try:
        response = requests.get(f"{api_base_url}/ai-agent/status", timeout=300)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ AI Agent: {status['status'].upper()}")
            print(f"   🔧 Tools Available: {status['tools_available']}")
            print(f"   🧠 Workflow Engine: {status['workflow_engine']}")
        else:
            print(f"   ❌ AI Agent offline or not responding")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to AI Agent: {e}")
        return
    
    # Get available operations
    print("\n2. Available AI Operations...")
    try:
        response = requests.get(f"{api_base_url}/ai-agent/operations", timeout=300)
        if response.status_code == 200:
            operations = response.json()
            for op in operations['supported_operations']:
                print(f"   🎯 {op['name']}: {op['description']}")
        else:
            print("   ❌ Could not fetch operations")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check for projects
    print("\n3. Checking for Projects...")
    try:
        response = requests.get(f"{api_base_url}/projects", timeout=5)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project = projects[0]
                print(f"   📋 Found project: {project['title']}")
                
                # Check for complex tasks
                response = requests.get(f"{api_base_url}/tasks?project_id={project['id']}", timeout=5)
                if response.status_code == 200:
                    tasks = response.json()
                    complex_tasks = [task for task in tasks 
                                   if task.get('estimated_time', 0) > 30 or len(task.get('title', '')) > 50]
                    
                    if complex_tasks:
                        task = complex_tasks[0]
                        print(f"   🎯 Found complex task: {task['title']}")
                        print(f"   ⏱️ Estimated time: {task.get('estimated_time', 15)} minutes")
                        
                        # Demo AI split
                        demo_task_split(api_base_url, task)
                    else:
                        print("   ℹ️ No complex tasks found (create tasks > 30 min to see AI splitting)")
                else:
                    print("   ❌ Could not fetch tasks")
            else:
                print("   ℹ️ No projects found. Create a project with complex tasks to demo AI features.")
        else:
            print("   ❌ Could not fetch projects")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def demo_task_split(api_base_url: str, task: Dict):
    """Demonstrate AI task splitting"""
    print(f"\n4. AI Task Splitting Demo...")
    print(f"   🔍 Analyzing task: {task['title']}")
    
    # Create preview
    request_data = {
        "operation": "split_task",
        "task_ids": [task["id"]],
        "context": {
            "user_preference": "prefer smaller, manageable tasks",
            "work_style": "focused work sessions"
        }
    }
    
    try:
        print("   🧠 Sending to AI for analysis...")
        response = requests.post(f"{api_base_url}/ai-agent/preview", 
                               json=request_data, timeout=600)
        
        if response.status_code == 200:
            preview = response.json()
            print("   ✨ AI Analysis Complete!")
            print(f"   🎯 Confidence: {preview['confidence_score']:.0%}")
            print(f"   📊 Impact: {preview['estimated_impact']}")
            
            # Show proposed subtasks
            proposed_changes = preview.get('proposed_changes', [])
            create_action = next((change for change in proposed_changes 
                                if change.get("action") == "create_tasks"), None)
            
            if create_action:
                subtasks = create_action.get('tasks', [])
                print(f"\n   📝 Proposed {len(subtasks)} Subtasks:")
                for i, subtask in enumerate(subtasks, 1):
                    print(f"      {i}. {subtask.get('title', 'Untitled')}")
                    print(f"         ⏱️ {subtask.get('estimated_minutes', 15)} min")
                    print(f"         💡 {subtask.get('context', 'anytime')}")
                
                # Show reasoning
                reasoning = preview.get('reasoning', '').replace('\n', ' ')[:200]
                print(f"\n   🧠 AI Reasoning: {reasoning}...")
                
                print(f"\n   💡 In the desktop app, you would now see a beautiful dialog")
                print(f"      showing this analysis and asking for your approval!")
                print(f"      The preview_id '{preview['preview_id']}' would be used to execute.")
                
            else:
                print("   ℹ️ No subtasks were proposed")
                
        else:
            print(f"   ❌ AI Analysis failed: {response.status_code}")
            if response.text:
                try:
                    error = response.json().get('detail', response.text)
                    print(f"      Error: {error}")
                except:
                    print(f"      Response: {response.text[:100]}")
                    
    except requests.exceptions.Timeout:
        print("   ⏰ AI Analysis timed out (this is normal if AI model is starting up)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def create_demo_data(api_base_url: str):
    """Create demo project and complex task for testing"""
    print("\n🎯 Creating Demo Data...")
    
    # Create project
    project_data = {
        "title": "Website Redesign Project",
        "description": "Complete overhaul of company website with modern design",
        "location": "Remote"
    }
    
    try:
        response = requests.post(f"{api_base_url}/projects", json=project_data, timeout=5)
        if response.status_code == 200:
            project = response.json()
            print(f"   ✅ Created project: {project['title']}")
            
            # Create complex task
            task_data = {
                "project_id": project["id"],
                "title": "Implement comprehensive user authentication system with social login, password recovery, and user profile management",
                "description": "Build a complete user authentication system including user registration, login, logout, password reset via email, social media integration (Google, Facebook, GitHub), user profile editing, avatar upload, account verification, and security features like two-factor authentication and session management.",
                "priority": "high",
                "estimated_time": 240,  # 4 hours - perfect for splitting
                "energy_level": "high",
                "context": "when you have deep focus time and minimal interruptions"
            }
            
            response = requests.post(f"{api_base_url}/tasks", json=task_data, timeout=5)
            if response.status_code == 201:
                task = response.json()
                print(f"   ✅ Created complex task: {task['title'][:50]}...")
                print(f"   ⏱️ Estimated time: {task['estimated_time']} minutes")
                print(f"   🎯 This task is perfect for AI splitting!")
                return project, task
            else:
                print(f"   ❌ Failed to create task: {response.status_code}")
        else:
            print(f"   ❌ Failed to create project: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating demo data: {e}")
    
    return None, None

if __name__ == "__main__":
    print("Starting AI Features Demo...")
    print("Make sure the backend is running on http://127.0.0.1:8010")
    print()
    
    # Option to create demo data
    response = input("Create demo data for testing? (y/n): ").lower().strip()
    if response == 'y':
        api_base_url = "http://127.0.0.1:8010/api/v1"
        project, task = create_demo_data(api_base_url)
        if project and task:
            print(f"\n🎉 Demo data created! Now run the desktop app and:")
            print(f"   1. Select the '{project['title']}' project")
            print(f"   2. Look for the task with the 🤖 Auto Split button")
            print(f"   3. Click it to see the AI in action!")
    
    # Run main demo
    demo_ai_features()
    
    print("\n🎉 Demo complete!")
    print("💡 To see the full AI experience, run the desktop app and try splitting tasks!") 
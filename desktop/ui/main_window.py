"""
Motivate.AI Desktop - Main Window

Modern task and project management interface using CustomTkinter.
Features responsive design, project sidebar, and task management.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Optional
import requests
import os
import threading
from datetime import datetime, date
from .new_project import show_new_project_dialog

# Set appearance and theme
ctk.set_appearance_mode("light")  # "light" or "dark" or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"

class MainWindow:
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8010/api/v1")
        self.projects = []
        self.tasks = []
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Motivate.AI")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Setup UI immediately (non-blocking)
        self.setup_ui()
        
        # Load projects immediately (no async needed since window shows instantly)
        self.load_projects_data()
    
    def setup_ui(self):
        """Set up the main user interface (non-blocking)"""
        
        # Top toolbar
        self.create_toolbar()
        
        # Status bar (create early so other components can use it)
        self.create_status_bar()
        
        # Main content area with sidebar and task view
        self.create_main_content()
        
        # Show ready status
        self.status_label.configure(text="Ready")
    
    def load_projects_data(self):
        """Load projects data immediately (no threading needed)"""
        try:
            response = requests.get(f"{self.api_base_url}/projects", timeout=2)
            if response.status_code == 200:
                self.projects = response.json()
                status_text = f"Loaded {len(self.projects)} projects"
            else:
                self.projects = []
                status_text = "No projects found"
        except Exception as e:
            print(f"Could not load projects from backend: {e}")
            # Use demo data
            self.projects = [
                {"id": 1, "title": "Workshop Organization", "task_count": 5},
                {"id": 2, "title": "Garden Project", "task_count": 3},
                {"id": 3, "title": "3D Printing", "task_count": 7},
                {"id": 4, "title": "Learning Python", "task_count": 2}
            ]
            status_text = "Backend offline - showing demo data"
        
        # Update the projects UI immediately
        self.update_projects_ui()
        self.status_label.configure(text=status_text)
    
    def update_projects_ui(self):
        """Update the projects UI on the main thread"""
        # Clear existing projects
        for widget in self.projects_frame.winfo_children():
            widget.destroy()
        
        # Create project cards
        for project in self.projects:
            self.create_project_card(project)

    def create_toolbar(self):
        """Create the top toolbar with navigation and actions"""
        toolbar_frame = ctk.CTkFrame(self.root, height=60)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        toolbar_frame.grid_columnconfigure(1, weight=1)
        
        # App title and menu button
        title_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        menu_btn = ctk.CTkButton(title_frame, text="≡", width=40, height=40, 
                                command=self.toggle_sidebar, font=ctk.CTkFont(size=20))
        menu_btn.grid(row=0, column=0, padx=(0, 10))
        
        title_label = ctk.CTkLabel(title_frame, text="Motivate.AI", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=1)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        
        # Speech button
        self.speech_btn = ctk.CTkButton(actions_frame, text="🎤", width=40, height=40,
                                       command=self.voice_input, font=ctk.CTkFont(size=18))
        self.speech_btn.grid(row=0, column=0, padx=2)
        
        # Search button
        search_btn = ctk.CTkButton(actions_frame, text="🔍", width=40, height=40,
                                  command=self.toggle_search, font=ctk.CTkFont(size=18))
        search_btn.grid(row=0, column=1, padx=2)
        
        # Quick add button
        add_btn = ctk.CTkButton(actions_frame, text="➕", width=40, height=40,
                               command=self.quick_add_task, font=ctk.CTkFont(size=18))
        add_btn.grid(row=0, column=2, padx=2)
        
        # Settings button
        settings_btn = ctk.CTkButton(actions_frame, text="⚙️", width=40, height=40,
                                    command=self.open_settings, font=ctk.CTkFont(size=18))
        settings_btn.grid(row=0, column=3, padx=2)
    
    def create_main_content(self):
        """Create the main content area with sidebar and task view"""
        
        # Projects sidebar
        self.create_sidebar()
        
        # Main task view
        self.create_task_view()
    
    def create_sidebar(self):
        """Create the projects sidebar (without loading data)"""
        self.sidebar_frame = ctk.CTkFrame(self.root, width=280)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        self.sidebar_visible = True
        
        # Sidebar header
        sidebar_header = ctk.CTkLabel(self.sidebar_frame, text="Projects", 
                                     font=ctk.CTkFont(size=18, weight="bold"))
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        # Projects list (scrollable)
        self.projects_frame = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.projects_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Add project button
        add_project_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Project",
                                       command=self.add_project, height=35)
        add_project_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Note: load_projects_list() is now called asynchronously

    def create_task_view(self):
        """Create the main task view area"""
        self.task_frame = ctk.CTkFrame(self.root)
        self.task_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.task_frame.grid_rowconfigure(1, weight=1)
        
        # Task view header with filters
        self.create_task_header()
        
        # Main task list area
        self.task_list_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.task_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Load initial task view
        self.load_tasks_list()
    
    def create_task_header(self):
        """Create the task view header with filters and actions"""
        header_frame = ctk.CTkFrame(self.task_frame, height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Task filters
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Filter buttons
        all_btn = ctk.CTkButton(filter_frame, text="All", width=60, height=30,
                               command=lambda: self.filter_tasks("all"))
        all_btn.grid(row=0, column=0, padx=2)
        
        active_btn = ctk.CTkButton(filter_frame, text="Active", width=60, height=30,
                                  command=lambda: self.filter_tasks("active"))
        active_btn.grid(row=0, column=1, padx=2)
        
        completed_btn = ctk.CTkButton(filter_frame, text="Done", width=60, height=30,
                                     command=lambda: self.filter_tasks("completed"))
        completed_btn.grid(row=0, column=2, padx=2)
        
        # Task view title
        task_title = ctk.CTkLabel(header_frame, text="Tasks", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        task_title.grid(row=0, column=1, padx=20)
    
    def load_tasks_list(self):
        """Load and display tasks (placeholder for now)"""
        # Clear existing tasks
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        # Demo tasks
        demo_tasks = [
            "Clear workbench of old projects",
            "Organize tool drawers", 
            "Plan garden layout",
            "Research 3D printer settings"
        ]
        
        for i, task in enumerate(demo_tasks):
            self.create_task_item(i+1, task, completed=i % 3 == 0)
    
    def create_task_item(self, task_id, task_text, completed=False):
        """Create a task item in the task list"""
        task_frame = ctk.CTkFrame(self.task_list_frame, height=50)
        task_frame.grid(sticky="ew", padx=5, pady=2)
        task_frame.grid_columnconfigure(1, weight=1)
        
        # Task checkbox
        checkbox = ctk.CTkCheckBox(task_frame, text="", width=20, height=20,
                                  command=lambda: self.toggle_task_completion(task_id))
        checkbox.grid(row=0, column=0, padx=15, pady=15)
        if completed:
            checkbox.select()
        
        # Task text
        task_label = ctk.CTkLabel(task_frame, text=task_text, 
                                 font=ctk.CTkFont(size=14))
        task_label.grid(row=0, column=1, sticky="w", padx=10, pady=15)
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Starting up...", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=5)

    def load_projects_list(self):
        """Reload projects list (called when data changes)"""
        self.status_label.configure(text="Refreshing projects...")
        self.load_projects_data()
    
    def create_project_card(self, project):
        """Create a project card in the sidebar"""
        card_frame = ctk.CTkFrame(self.projects_frame, height=60)
        card_frame.grid(sticky="ew", padx=5, pady=2)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Project checkbox/icon
        checkbox = ctk.CTkCheckBox(card_frame, text="", width=20, height=20)
        checkbox.grid(row=0, column=0, padx=10, pady=15)
        
        # Project name and details
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        name_label = ctk.CTkLabel(details_frame, text=project["title"], 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        name_label.grid(row=0, column=0, sticky="w")
        
        task_count = project.get("task_count", 0)
        count_label = ctk.CTkLabel(details_frame, text=f"{task_count} tasks",
                                  font=ctk.CTkFont(size=12), text_color="gray")
        count_label.grid(row=1, column=0, sticky="w")
    
    # Event handlers
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.sidebar_frame.grid_remove()
            self.sidebar_visible = False
        else:
            self.sidebar_frame.grid()
            self.sidebar_visible = True
    
    def voice_input(self):
        """Handle voice input button"""
        self.status_label.configure(text="Voice input - Coming soon!")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def toggle_search(self):
        """Toggle search interface"""
        self.status_label.configure(text="Search - Coming soon!")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def quick_add_task(self):
        """Open quick add task dialog"""
        self.status_label.configure(text="Quick add - Coming soon!")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def open_settings(self):
        """Open settings window"""
        self.status_label.configure(text="Settings - Coming soon!")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def add_project(self):
        """Add new project"""
        try:
            show_new_project_dialog(
                parent=self.root,
                on_project_created=self.on_project_created
            )
        except Exception as e:
            print(f"Error opening new project dialog: {e}")
            self.status_label.configure(text="Error opening project dialog")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def on_project_created(self, project_data):
        """Handle when a new project is created"""
        print(f"New project created: {project_data['title']}")
        # Refresh the projects list
        self.load_projects_list()
        # Update status
        self.status_label.configure(text=f"Project '{project_data['title']}' created successfully!")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def filter_tasks(self, filter_type):
        """Filter tasks by type"""
        self.status_label.configure(text=f"Filtering by: {filter_type}")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def toggle_task_completion(self, task_id):
        """Toggle task completion status"""
        self.status_label.configure(text=f"Task {task_id} completion toggled")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def load_data(self):
        """Load initial data (now just a placeholder)"""
        self.status_label.configure(text="Loading data...")
        self.root.after(1000, lambda: self.status_label.configure(text="Ready"))
    
    def run(self):
        """Start the main window"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run() 
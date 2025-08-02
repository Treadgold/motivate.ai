"""
Motivate.AI Desktop - Main Window

Modern task and project management interface using CustomTkinter.
Features responsive design, resizable project sidebar, and task management.
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
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.projects = []
        self.tasks = []
        self.selected_project = None
        self.selected_project_id = None
        self.pending_updates = []  # Store updates when window isn't ready
        
        # Load settings first
        self.load_and_apply_settings()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Motivate.AI")
        self.root.geometry("1450x900")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_rowconfigure(1, weight=2)
        
        # Setup UI immediately (non-blocking)
        self.setup_ui()
        
        # Load projects immediately (no async needed since window shows instantly)
        self.load_projects_data()
    
    def load_and_apply_settings(self):
        """Load and apply settings from file"""
        try:
            from .settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(None)  # No parent needed for loading
            
            # Apply appearance settings
            theme = settings_dialog.settings["appearance"]["theme"]
            if theme != "system":
                ctk.set_appearance_mode(theme)
            
            color_theme = settings_dialog.settings["appearance"]["color_theme"]
            ctk.set_default_color_theme(color_theme)
            
            # Update API base URL if different from default
            saved_api_url = settings_dialog.settings["api"]["base_url"]
            if saved_api_url != "http://127.0.0.1:8010/api/v1":
                self.api_base_url = saved_api_url
                os.environ["API_BASE_URL"] = saved_api_url
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Continue with defaults
    
    def setup_ui(self):
        """Set up the main user interface (non-blocking)"""
        
        # Top toolbar
        self.create_toolbar()
        
        # Status bar (create early so other components can use it)
        self.create_status_bar()
        
        # Main content area with resizable sidebar and task view
        self.create_main_content()
        
        # Show ready status
        self.status_label.configure(text="Ready")
    
    def load_projects_data(self):
        """Load projects data asynchronously (non-blocking)"""
        # Show loading state immediately
        self.projects = []
        self.update_projects_ui()
        self.status_label.configure(text="Loading projects...")
        
        # Load real projects from API in background
        def load_projects_async():
            try:
                response = requests.get(f"{self.api_base_url}/projects", timeout=10)
                if response.status_code == 200:
                    real_projects = response.json()
                    # Update UI on main thread safely
                    self.safe_ui_update(lambda: self.update_projects_from_api(real_projects))
                else:
                    self.safe_ui_update(lambda: self.status_label.configure(text="No projects found"))
            except Exception as e:
                print(f"Could not load projects from backend: {e}")
                self.safe_ui_update(lambda: self.status_label.configure(text="Backend offline - cannot load projects"))
        
        # Start background loading
        thread = threading.Thread(target=load_projects_async, daemon=True)
        thread.start()
    
    def safe_ui_update(self, callback):
        """Safely update UI from background thread"""
        import threading
        
        # Always use pending queue for background threads to avoid RuntimeError
        if threading.current_thread() != threading.main_thread():
            self.pending_updates.append(callback)
        else:
            # If we're on the main thread, execute immediately
            try:
                if self.root and self.root.winfo_exists():
                    callback()
                else:
                    # If window doesn't exist, store the update for later
                    self.pending_updates.append(callback)
            except Exception as e:
                print(f"Could not update UI: {e}")
                # Store the update for later as fallback
                self.pending_updates.append(callback)
    
    def process_pending_updates(self):
        """Process any pending UI updates (call when window is shown)"""
        while self.pending_updates:
            try:
                callback = self.pending_updates.pop(0)
                callback()
            except Exception as e:
                print(f"Error processing pending update: {e}")
    
    def show_window(self):
        """Show the main window and process any pending updates"""
        if self.root:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            # Process any updates that were waiting
            self.process_pending_updates()
    
    def update_projects_from_api(self, real_projects):
        """Update projects with real data from API (called on main thread)"""
        self.projects = real_projects
        self.update_projects_ui()
        
        # Update task detail pane project dropdown if it exists
        if hasattr(self, 'project_combo') and self.project_combo:
            project_names = [p.get("title", "Unknown") for p in self.projects]
            if not project_names:
                project_names = ["General Tasks"]
            self.project_combo.configure(values=project_names)
            
            # Set to currently selected project if available
            if self.selected_project:
                self.project_combo.set(self.selected_project.get("title", "General Tasks"))
            elif project_names:
                self.project_combo.set(project_names[0])
        
        self.status_label.configure(text=f"Loaded {len(self.projects)} projects")
    
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
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
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
        
        # Quick add button - Now functional!
        add_btn = ctk.CTkButton(actions_frame, text="➕", width=40, height=40,
                               command=self.quick_add_task, font=ctk.CTkFont(size=18))
        add_btn.grid(row=0, column=2, padx=2)
        
        # AI Status indicator
        self.ai_status_btn = ctk.CTkButton(actions_frame, text="🤖", width=40, height=40,
                                          command=self.check_ai_status,
                                          font=ctk.CTkFont(size=18),
                                          fg_color=("gray", "gray40"),
                                          hover_color=("darkgray", "gray60"))
        self.ai_status_btn.grid(row=0, column=3, padx=2)
        
        # Settings button
        settings_btn = ctk.CTkButton(actions_frame, text="⚙️", width=40, height=40,
                                    command=self.open_settings, font=ctk.CTkFont(size=18))
        settings_btn.grid(row=0, column=4, padx=2)
        
        # Check AI status after main loop starts
        self.root.after(1000, self.check_ai_status_background)
    
    def create_main_content(self):
        """Create the main content area with resizable sidebar, task view, and task detail pane"""
        
        # Create a main container for the paned window
        main_container = ctk.CTkFrame(self.root)
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Use tkinter PanedWindow for resizable splitter
        self.paned_window = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, 
                                          sashwidth=12, sashrelief="raised",
                                          bg="#212108")
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        
        # Projects sidebar
        self.create_sidebar()
        
        # Main task view
        self.create_task_view()
        
        # Task detail/edit pane
        self.create_task_detail_pane()
        
        # Add all three panels to the paned window
        self.paned_window.add(self.sidebar_frame, minsize=380, width=620)
        self.paned_window.add(self.task_frame, minsize=500)
        self.paned_window.add(self.task_detail_frame, minsize=450, width=450)
        
        self.sidebar_visible = True
        self.task_detail_visible = True
        self.selected_task = None
        self.editing_task = False
    
    def create_sidebar(self):
        """Create the projects sidebar (without loading data)"""
        self.sidebar_frame = ctk.CTkFrame(self.paned_window)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)  # Allow sidebar to expand horizontally
        
        # Sidebar header
        sidebar_header = ctk.CTkLabel(self.sidebar_frame, text="Projects", 
                                     font=ctk.CTkFont(size=18, weight="bold"))
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        # Projects list (scrollable)
        self.projects_frame = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.projects_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.projects_frame.grid_columnconfigure(0, weight=1)  # Allow projects frame to expand
        
        # Add project button
        add_project_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Project",
                                       command=self.add_project, height=35)
        add_project_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

    def create_task_view(self):
        """Create the main task view area"""
        self.task_frame = ctk.CTkFrame(self.paned_window)
        self.task_frame.grid_rowconfigure(1, weight=1)
        self.task_frame.grid_columnconfigure(0, weight=1)  # Allow task frame to expand horizontally
        
        # Task view header with filters
        self.create_task_header()
        
        # Main task list area
        self.task_list_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.task_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.task_list_frame.grid_columnconfigure(0, weight=1)  # Allow task list items to expand
        
        # Load initial task view (empty state)
        self.load_tasks_list()

    def create_task_detail_pane(self):
        """Create the task detail/edit pane on the right side"""
        self.task_detail_frame = ctk.CTkFrame(self.paned_window)
        self.task_detail_frame.grid_rowconfigure(1, weight=1)
        self.task_detail_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_task_detail_header()
        
        # Scrollable content area
        self.task_detail_content = ctk.CTkScrollableFrame(self.task_detail_frame)
        self.task_detail_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.task_detail_content.grid_columnconfigure(0, weight=1)
        
        # Initially show the new task form
        self.show_new_task_form()
        
    def create_task_detail_header(self):
        """Create the task detail pane header"""
        header_frame = ctk.CTkFrame(self.task_detail_frame, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title that changes based on mode
        self.task_detail_title = ctk.CTkLabel(header_frame, text="➕ New Task", 
                                            font=ctk.CTkFont(size=18, weight="bold"))
        self.task_detail_title.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)
        
        # Save button
        self.save_btn = ctk.CTkButton(button_frame, text="💾 Save", width=80, height=35,
                                     command=self.save_task,
                                     fg_color=("green", "darkgreen"), 
                                     hover_color=("darkgreen", "green"))
        self.save_btn.grid(row=0, column=0, padx=2)
        
        # Cancel/Clear button
        self.cancel_btn = ctk.CTkButton(button_frame, text="✖ Clear", width=80, height=35,
                                       command=self.clear_task_form,
                                       fg_color=("gray", "gray40"), 
                                       hover_color=("darkgray", "gray60"))
        self.cancel_btn.grid(row=0, column=1, padx=2)
        
    def show_new_task_form(self):
        """Display the new task creation form"""
        # Clear existing content
        for widget in self.task_detail_content.winfo_children():
            widget.destroy()
            
        # Task title
        ctk.CTkLabel(self.task_detail_content, text="Task Title:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(15, 5))
        
        self.title_entry = ctk.CTkEntry(self.task_detail_content, height=40, 
                                       placeholder_text="What needs to be done?",
                                       font=ctk.CTkFont(size=13))
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 15))
        
        # Description
        ctk.CTkLabel(self.task_detail_content, text="Description:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(0, 5))
        
        self.desc_entry = ctk.CTkTextbox(self.task_detail_content, height=80, 
                                        font=ctk.CTkFont(size=12))
        self.desc_entry.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 15))
        
        # Project selection
        ctk.CTkLabel(self.task_detail_content, text="Project:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=4, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Get project names for dropdown
        project_names = [p.get("title", "Unknown") for p in self.projects]
        if not project_names:
            project_names = ["General Tasks"]
        
        self.project_combo = ctk.CTkComboBox(self.task_detail_content, values=project_names, 
                                            height=35, font=ctk.CTkFont(size=13))
        self.project_combo.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 15))
        
        # Set default project to currently selected project
        if self.selected_project:
            self.project_combo.set(self.selected_project.get("title", "General Tasks"))
        else:
            self.project_combo.set(project_names[0])
        
        # Time and Priority row
        details_frame = ctk.CTkFrame(self.task_detail_content, fg_color="transparent")
        details_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=(0, 15))
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Time
        time_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        time_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        time_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(time_frame, text="Time (min):", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.time_var = tk.StringVar(value="15")
        self.time_entry = ctk.CTkEntry(time_frame, height=35, textvariable=self.time_var,
                                      font=ctk.CTkFont(size=13))
        self.time_entry.grid(row=1, column=0, sticky="ew")
        
        # Priority
        priority_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        priority_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        priority_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(priority_frame, text="Priority:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.priority_var = tk.StringVar(value="Normal")
        self.priority_combo = ctk.CTkComboBox(priority_frame, 
                                             values=["Low", "Normal", "High", "Urgent"],
                                             variable=self.priority_var, height=35,
                                             font=ctk.CTkFont(size=13))
        self.priority_combo.grid(row=1, column=0, sticky="ew")
        
        # Status (for editing existing tasks)
        self.status_frame = ctk.CTkFrame(self.task_detail_content, fg_color="transparent")
        # Initially hidden for new tasks
        
        ctk.CTkLabel(self.status_frame, text="Status:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(15, 5))
        
        self.status_var = tk.StringVar(value="pending")
        self.status_combo = ctk.CTkComboBox(self.status_frame, 
                                           values=["pending", "in_progress", "completed", "cancelled"],
                                           variable=self.status_var, height=35,
                                           font=ctk.CTkFont(size=13))
        self.status_combo.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Set editing mode flags
        self.editing_task = False
        self.selected_task = None
        self.task_detail_title.configure(text="➕ New Task")
        self.cancel_btn.configure(text="✖ Clear")

    def clear_task_form(self):
        """Clear the task form and reset to new task mode"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete("0.0", tk.END)
        self.time_var.set("15")
        self.priority_var.set("Normal")
        self.status_var.set("pending")
        
        # Reset to new task mode
        self.editing_task = False
        self.selected_task = None
        self.task_detail_title.configure(text="➕ New Task")
        self.cancel_btn.configure(text="✖ Clear")
        
        # Hide status frame for new tasks
        self.status_frame.grid_remove()
        
        # Set project to currently selected if available
        if self.selected_project:
            self.project_combo.set(self.selected_project.get("title", "General Tasks"))
        
        # Focus on title
        self.title_entry.focus()
    
    def save_task(self):
        """Save the current task (new or edited)"""
        # Get form data
        title = self.title_entry.get().strip()
        description = self.desc_entry.get("0.0", tk.END).strip()
        project_title = self.project_combo.get()
        time_minutes = self.time_var.get()
        priority = self.priority_var.get()
        status = self.status_var.get()
        
        # Validate required fields
        if not title:
            self.status_label.configure(text="Error: Task title is required")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
            return
        
        # Find project ID
        project_id = None
        for project in self.projects:
            if project.get("title") == project_title:
                project_id = project.get("id")
                break
        
        if not project_id and self.projects:
            project_id = self.projects[0].get("id")  # Default to first project
        
        # Prepare task data
        task_data = {
            "title": title,
            "description": description,
            "project_id": project_id,
            "estimated_time": int(time_minutes) if time_minutes.isdigit() else 15,
            "priority": priority.lower(),
            "status": status
        }
        
        try:
            if self.editing_task and self.selected_task:
                # Update existing task
                task_id = self.selected_task.get("id")
                response = requests.put(f"{self.api_base_url}/tasks/{task_id}", 
                                      json=task_data, timeout=5)
                if response.status_code == 200:
                    self.status_label.configure(text="Task updated successfully!")
                    self.load_tasks_list(self.selected_project_id)  # Refresh task list
                    self.clear_task_form()  # Reset to new task mode
                else:
                    self.status_label.configure(text="Error updating task")
            else:
                # Create new task
                response = requests.post(f"{self.api_base_url}/tasks", 
                                       json=task_data, timeout=5)
                if response.status_code == 201:
                    self.status_label.configure(text="Task created successfully!")
                    self.load_tasks_list(self.selected_project_id)  # Refresh task list
                    self.clear_task_form()  # Clear form for next task
                else:
                    self.status_label.configure(text="Error creating task")
                    
        except requests.exceptions.RequestException:
            self.status_label.configure(text="Error: Could not connect to server")
        
        # Clear status after 3 seconds
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))

    def edit_task(self, task):
        """Load a task into the detail pane for editing"""
        self.selected_task = task
        self.editing_task = True
        
        # Update header
        self.task_detail_title.configure(text="✏️ Edit Task")
        self.cancel_btn.configure(text="✖ Cancel")
        
        # Populate form fields
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, task.get("title", ""))
        
        self.desc_entry.delete("0.0", tk.END)
        self.desc_entry.insert("0.0", task.get("description", ""))
        
        # Set project
        project_title = "General Tasks"
        for project in self.projects:
            if project.get("id") == task.get("project_id"):
                project_title = project.get("title", "General Tasks")
                break
        self.project_combo.set(project_title)
        
        # Set time, priority, and status
        self.time_var.set(str(task.get("estimated_time", 15)))
        self.priority_var.set(task.get("priority", "normal").title())
        self.status_var.set(task.get("status", "pending"))
        
        # Show status field for editing
        self.status_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=(0, 15))
        
        # Focus on title for editing
        self.title_entry.focus()
    
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
        
        # Task view title - shows selected project
        self.task_title = ctk.CTkLabel(header_frame, text="Select a project to view tasks", 
                                      font=ctk.CTkFont(size=18, weight="bold"))
        self.task_title.grid(row=0, column=1, padx=20)
    
    def load_tasks_list(self, project_id=None):
        """Load and display tasks for the selected project"""
        # Clear existing tasks immediately
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        if project_id is None:
            # Show empty state
            empty_label = ctk.CTkLabel(self.task_list_frame, 
                                      text="Select a project from the sidebar to view its tasks",
                                      font=ctk.CTkFont(size=16),
                                      text_color="gray")
            empty_label.grid(pady=50)
            return

        # Show loading state immediately for instant feedback
        loading_label = ctk.CTkLabel(self.task_list_frame, 
                                    text="Loading tasks...",
                                    font=ctk.CTkFont(size=16),
                                    text_color="gray")
        loading_label.grid(pady=50)

        # Load real tasks from backend in background thread
        def load_tasks_async():
            try:
                response = requests.get(f"{self.api_base_url}/tasks?project_id={project_id}", timeout=10)
                if response.status_code == 200:
                    real_tasks = response.json()
                    # Update UI on main thread safely with real data
                    self.safe_ui_update(lambda: self.update_tasks_ui(real_tasks, project_id))
                else:
                    # No tasks found on server
                    self.safe_ui_update(lambda: self.show_no_tasks_message())
                    
            except Exception as e:
                print(f"Could not load tasks from backend: {e}")
                # Show offline message
                self.safe_ui_update(lambda: self.show_offline_message())
        
        # Start background loading of real data
        thread = threading.Thread(target=load_tasks_async, daemon=True)
        thread.start()
    
    def show_no_tasks_message(self):
        """Show message when no tasks are found"""
        # Clear loading message
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        empty_label = ctk.CTkLabel(self.task_list_frame, 
                                  text="No tasks in this project yet.\nClick the ➕ button to add some!",
                                  font=ctk.CTkFont(size=16),
                                  text_color="gray")
        empty_label.grid(pady=50)
    
    def show_offline_message(self):
        """Show message when backend is offline"""
        # Clear loading message
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        offline_label = ctk.CTkLabel(self.task_list_frame, 
                                    text="Cannot connect to backend.\nPlease check your connection and try again.",
                                    font=ctk.CTkFont(size=16),
                                    text_color="red")
        offline_label.grid(pady=50)
    
    def update_tasks_ui(self, tasks, project_id):
        """Update the tasks UI on the main thread"""
        # Clear loading message
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # Store tasks
        self.tasks = tasks

        # Create task items
        if self.tasks:
            for task in self.tasks:
                self.create_task_item(task)
        else:
            empty_label = ctk.CTkLabel(self.task_list_frame, 
                                      text="No tasks in this project yet.\nClick the ➕ button to add some!",
                                      font=ctk.CTkFont(size=16),
                                      text_color="gray")
            empty_label.grid(pady=50)
    
    def create_task_item(self, task):
        """Create a clickable task item in the task list with AI split button"""
        # Calculate dynamic height based on content
        base_height = 80
        description = task.get("description", "")
        if description and len(description) > 50:
            base_height = 100  # Increase height for tasks with descriptions
            
        task_frame = ctk.CTkFrame(self.task_list_frame, height=base_height)
        task_frame.grid(sticky="ew", padx=5, pady=2)
        task_frame.grid_columnconfigure(1, weight=1)  # Content expands
        task_frame.grid_columnconfigure(2, weight=0)  # Actions stay fixed
        
        # Make the entire task clickable for editing
        task_frame.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        # Task checkbox
        is_completed = task.get("status") == "completed"
        checkbox = ctk.CTkCheckBox(task_frame, text="", width=20, height=20,
                                  command=lambda t=task: self.toggle_task_completion(t))
        checkbox.grid(row=0, column=0, padx=15, pady=25, sticky="n")
        if is_completed:
            checkbox.select()
        
        # Task content area - now with better expansion
        content_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        # Task title with text wrapping and strikethrough for completed tasks
        task_text = task.get("title", "Untitled Task")
        if is_completed:
            task_text = f"~~{task_text}~~"  # Add strikethrough effect
            text_color = "gray60"
            font_weight = "normal"
        else:
            text_color = None
            font_weight = "bold"
            
        task_label = ctk.CTkLabel(content_frame, text=task_text, 
                                 font=ctk.CTkFont(size=14, weight=font_weight),
                                 text_color=text_color,
                                 wraplength=400)  # Wrap long titles
        task_label.grid(row=0, column=0, sticky="w")
        task_label.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        # Task description with wrapping (if present)
        if description:
            desc_label = ctk.CTkLabel(content_frame, text=description[:100] + ("..." if len(description) > 100 else ""), 
                                    font=ctk.CTkFont(size=11),
                                    text_color="gray60",
                                    wraplength=400)
            desc_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
            desc_label.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        # Task details (priority, time, etc.)
        details_text = []
        if task.get("priority") and task.get("priority") != "normal":
            details_text.append(f"Priority: {task.get('priority').title()}")
        if task.get("estimated_time"):
            details_text.append(f"{task.get('estimated_time')} min")
        
        if details_text:
            details_row = 2 if description else 1
            details_label = ctk.CTkLabel(content_frame, text=" • ".join(details_text), 
                                       font=ctk.CTkFont(size=11),
                                       text_color="gray")
            details_label.grid(row=details_row, column=0, sticky="w", pady=(2, 0))
            details_label.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        # Action buttons frame (only show for non-completed tasks)
        if not is_completed:
            actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=2, padx=10, pady=15, sticky="ne")  # Anchor to top-right
            
            # AI Auto Split Task button - show for most tasks to make it discoverable
            estimated_time = task.get("estimated_time", 0)
            if estimated_time > 15 or len(task.get("title", "")) > 25:  # Lower threshold for better visibility
                ai_split_btn = ctk.CTkButton(actions_frame, text="🤖 Split Task", 
                                           width=110, height=30,
                                           command=lambda t=task: self.show_ai_split_dialog(t),
                                           fg_color=("#1f538d", "#14375e"),  # More vibrant blue
                                           hover_color=("#2563eb", "#1d4ed8"),
                                           font=ctk.CTkFont(size=12, weight="bold"))
                ai_split_btn.grid(row=0, column=0, padx=2)
                
                # Add tooltip for better UX
                self.add_ai_tooltip(ai_split_btn, task)
            else:
                # Show a subtle AI icon for smaller tasks
                ai_hint_btn = ctk.CTkButton(actions_frame, text="🤖", 
                                          width=35, height=30,
                                          command=lambda t=task: self.show_ai_split_dialog(t),
                                          fg_color=("#1f538d", "#14375e"),
                                          hover_color=("#2563eb", "#1d4ed8"),
                                          font=ctk.CTkFont(size=14))
                ai_hint_btn.grid(row=0, column=0, padx=2)
                
                # Add tooltip for clarity
                self.add_ai_tooltip(ai_hint_btn, task)
            
            # Edit button
            edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=35, height=30,
                                   command=lambda t=task: self.edit_task(t),
                                   fg_color=("gray", "gray40"),
                                   hover_color=("darkgray", "gray60"),
                                   font=ctk.CTkFont(size=12))
            edit_btn.grid(row=0, column=1, padx=2)
            
            # Delete button
            delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=35, height=30,
                                     command=lambda t=task: self.delete_task(t),
                                     fg_color=("red", "darkred"),
                                     hover_color=("darkred", "red"),
                                     font=ctk.CTkFont(size=12))
            delete_btn.grid(row=0, column=2, padx=2)
        
        # Add hover effect
        def on_enter(e):
            task_frame.configure(fg_color=("gray70", "gray30"))
        def on_leave(e):
            task_frame.configure(fg_color=("gray90", "gray13"))
            
        task_frame.bind("<Enter>", on_enter)
        task_frame.bind("<Leave>", on_leave)
    
    def toggle_task_completion(self, task):
        """Toggle task completion status"""
        current_status = task.get("status", "pending")
        new_status = "completed" if current_status != "completed" else "pending"
        
        try:
            # Update task status via API
            task_id = task.get("id")
            task_data = {"status": new_status}
            response = requests.put(f"{self.api_base_url}/tasks/{task_id}", 
                                    json=task_data, timeout=5)
            
            if response.status_code == 200:
                # Update local task data
                task["status"] = new_status
                
                # If this task is currently being edited, update the form
                if self.editing_task and self.selected_task and self.selected_task.get("id") == task_id:
                    self.status_var.set(new_status)
                
                # Refresh the task list to show updated status
                self.load_tasks_list(self.selected_project_id)
                
                status_text = "completed" if new_status == "completed" else "active"
                self.status_label.configure(text=f"Task marked as {status_text}")
            else:
                self.status_label.configure(text="Error updating task status")
                
        except requests.exceptions.RequestException:
            self.status_label.configure(text="Error: Could not connect to server")
        
        # Clear status after 3 seconds
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def delete_task(self, task):
        """Delete a task with confirmation dialog"""
        import tkinter.messagebox as msgbox
        
        task_title = task.get("title", "Untitled Task")
        
        # Show confirmation dialog
        result = msgbox.askyesno(
            "Delete Task",
            f"Are you sure you want to delete the task:\n\n'{task_title}'\n\nThis action cannot be undone.",
            icon='warning'
        )
        
        if result:
            try:
                task_id = task.get("id")
                response = requests.delete(f"{self.api_base_url}/tasks/{task_id}", timeout=5)
                
                if response.status_code == 200:
                    self.status_label.configure(text=f"Task '{task_title}' deleted successfully")
                    
                    # If this task is currently being edited, clear the edit pane
                    if self.editing_task and self.selected_task and self.selected_task.get("id") == task_id:
                        self.clear_task_form()
                        self.editing_task = False
                        self.selected_task = None
                    
                    # Refresh the task list
                    self.load_tasks_list(self.selected_project_id)
                else:
                    self.status_label.configure(text="Error deleting task")
                    
            except requests.exceptions.RequestException:
                self.status_label.configure(text="Error: Could not connect to server")
            
            # Clear status after 3 seconds
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def delete_project(self, project):
        """Delete a project with confirmation dialog"""
        import tkinter.messagebox as msgbox
        
        project_title = project.get("title", "Untitled Project")
        task_count = project.get("task_count", 0)
        
        # Show confirmation dialog with task count warning
        warning_text = f"Are you sure you want to delete the project:\n\n'{project_title}'"
        if task_count > 0:
            warning_text += f"\n\nThis project contains {task_count} task(s) that will also be deleted."
        warning_text += "\n\nThis action cannot be undone."
        
        result = msgbox.askyesno(
            "Delete Project",
            warning_text,
            icon='warning'
        )
        
        if result:
            try:
                project_id = project.get("id")
                response = requests.delete(f"{self.api_base_url}/projects/{project_id}", timeout=5)
                
                if response.status_code == 200:
                    self.status_label.configure(text=f"Project '{project_title}' deleted successfully")
                    
                    # If this was the selected project, clear the task view
                    if self.selected_project_id == project_id:
                        self.selected_project = None
                        self.selected_project_id = None
                        self.task_title.configure(text="Tasks")
                        self.load_tasks_list()  # Load empty state
                        
                        # Clear task edit form if open
                        if self.editing_task:
                            self.clear_task_form()
                            self.editing_task = False
                            self.selected_task = None
                    
                    # Refresh the projects list
                    self.load_projects_list()
                else:
                    self.status_label.configure(text="Error deleting project")
                    
            except requests.exceptions.RequestException:
                self.status_label.configure(text="Error: Could not connect to server")
            
            # Clear status after 3 seconds
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Starting up...", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=5)

    def load_projects_list(self):
        """Reload projects list (called when data changes)"""
        self.status_label.configure(text="Refreshing projects...")
        self.load_projects_data()
    
    def create_project_card(self, project):
        """Create a clickable project card in the sidebar"""
        card_frame = ctk.CTkFrame(self.projects_frame, height=60)
        card_frame.grid(row=len(self.projects_frame.winfo_children()), column=0, sticky="ew", padx=5, pady=2)
        card_frame.grid_columnconfigure(1, weight=1)
        card_frame.grid_columnconfigure(2, weight=0)  # Actions column
        
        # Make the entire card clickable
        card_frame.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project checkbox/icon
        checkbox = ctk.CTkCheckBox(card_frame, text="", width=20, height=20)
        checkbox.grid(row=0, column=0, padx=10, pady=15)
        checkbox.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project name and details
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        details_frame.grid_columnconfigure(0, weight=1)  # Allow details to expand
        details_frame.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        name_label = ctk.CTkLabel(details_frame, text=project["title"], 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        name_label.grid(row=0, column=0, sticky="w")
        name_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        task_count = project.get("task_count", 0)
        count_label = ctk.CTkLabel(details_frame, text=f"{task_count} tasks",
                                  font=ctk.CTkFont(size=12), text_color="gray")
        count_label.grid(row=1, column=0, sticky="w")
        count_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project delete button
        delete_btn = ctk.CTkButton(card_frame, text="🗑️", width=30, height=30,
                                 command=lambda p=project: self.delete_project(p),
                                 fg_color=("red", "darkred"),
                                 hover_color=("darkred", "red"),
                                 font=ctk.CTkFont(size=12))
        delete_btn.grid(row=0, column=2, padx=5, pady=15)
        
        # Store reference for highlighting
        card_frame.project_id = project["id"]
    
    def select_project(self, project):
        """Select a project and load its tasks"""
        self.selected_project = project
        self.selected_project_id = project["id"]
        
        # Update task header title
        self.task_title.configure(text=f"Tasks: {project['title']}")
        
        # Highlight selected project
        self.highlight_selected_project()
        
        # Load tasks for this project
        self.load_tasks_list(project["id"])
        
        # Update status
        self.status_label.configure(text=f"Selected project: {project['title']}")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def highlight_selected_project(self):
        """Highlight the currently selected project"""
        for widget in self.projects_frame.winfo_children():
            if hasattr(widget, 'project_id'):
                if widget.project_id == self.selected_project_id:
                    widget.configure(fg_color=("gray70", "gray30"))  # Highlighted
                else:
                    widget.configure(fg_color=("gray90", "gray13"))  # Normal

    # Event handlers
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.paned_window.forget(self.sidebar_frame)
            self.sidebar_visible = False
        else:
            self.paned_window.add(self.sidebar_frame, minsize=250, width=640, before=self.task_frame)
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
        """Focus on the inline task editor for adding a new task"""
        # Clear and focus the task detail pane for new task entry
        self.clear_task_form()
        self.title_entry.focus()
        
        # Update status
        self.status_label.configure(text="Ready to add new task")
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def open_settings(self):
        """Open settings window"""
        try:
            from .settings_dialog import show_settings_dialog
            
            def on_settings_saved(settings):
                """Handle when settings are saved"""
                # Update API base URL if changed
                if settings["api"]["base_url"] != self.api_base_url:
                    self.api_base_url = settings["api"]["base_url"]
                    # Reload projects with new API URL
                    self.load_projects_data()
                
                # Update status
                self.status_label.configure(text="Settings updated successfully!")
                self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
            
            show_settings_dialog(self.root, on_settings_saved)
            
        except Exception as e:
            print(f"Error opening settings dialog: {e}")
            self.status_label.configure(text="Error opening settings")
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
    
    def load_data(self):
        """Load initial data (now just a placeholder)"""
        self.status_label.configure(text="Loading data...")
        self.root.after(1000, lambda: self.status_label.configure(text="Ready"))
    
    def show_ai_split_dialog(self, task):
        """Show the AI split task dialog"""
        try:
            # Immediate feedback in status bar
            self.status_label.configure(text="🤖 Starting AI analysis - this may take 10-30 seconds...")
            
            from .ai_split_dialog import show_ai_split_dialog
            
            def on_approve(preview_data):
                """Handle when user approves the AI split"""
                self.execute_ai_split(preview_data)
            
            def on_cancel():
                """Handle when user cancels the AI split"""
                self.status_label.configure(text="AI task splitting cancelled")
                self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
            
            # Show the AI dialog
            show_ai_split_dialog(self.root, task, on_approve, on_cancel)
            
        except Exception as e:
            print(f"Error showing AI split dialog: {e}")
            self.status_label.configure(text="Error: Could not open AI assistant")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def execute_ai_split(self, preview_data):
        """Execute the AI split after user approval"""
        try:
            preview_id = preview_data.get("preview_id")
            if not preview_id:
                self.status_label.configure(text="Error: Invalid preview data")
                return
            
            # Show executing status
            self.status_label.configure(text="🤖 Executing AI task split...")
            
            # Execute in background thread to avoid blocking UI
            def execute_split():
                try:
                    response = requests.post(f"{self.api_base_url}/ai-agent/execute/{preview_id}", 
                                           timeout=600)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            # Success! Update UI on main thread safely
                            self.safe_ui_update(lambda: self.on_split_success(result))
                        else:
                            error_msg = result.get("error_message", "Unknown error")
                            self.safe_ui_update(lambda: self.on_split_error(f"Split failed: {error_msg}"))
                    else:
                        self.safe_ui_update(lambda: self.on_split_error(f"API Error: {response.status_code}"))
                        
                except requests.exceptions.Timeout:
                    self.safe_ui_update(lambda: self.on_split_error("Split timed out"))
                except requests.exceptions.ConnectionError:
                    self.safe_ui_update(lambda: self.on_split_error("Cannot connect to AI service"))
                except Exception as e:
                    self.safe_ui_update(lambda: self.on_split_error(f"Unexpected error: {str(e)}"))
            
            # Start execution in background
            thread = threading.Thread(target=execute_split, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error executing AI split: {e}")
            self.status_label.configure(text="Error executing split")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def on_split_success(self, result):
        """Handle successful AI split execution"""
        # Refresh the task list to show new subtasks
        if self.selected_project_id:
            self.load_tasks_list(self.selected_project_id)
        
        # Show success message
        executed_changes = result.get("executed_changes", [])
        created_count = sum(1 for change in executed_changes if change.get("action") == "created_tasks")
        
        self.status_label.configure(text=f"✨ AI split complete! Created {created_count} subtasks")
        self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
        
        # Show success notification
        self.show_success_notification("Task split successfully!", 
                                     f"Your task has been intelligently divided into {created_count} manageable subtasks")
    
    def on_split_error(self, error_message):
        """Handle AI split execution error"""
        self.status_label.configure(text=f"❌ Split failed: {error_message}")
        self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
        
        # Could add error notification here
        print(f"AI split error: {error_message}")
    
    def show_success_notification(self, title, message):
        """Show a success notification popup"""
        try:
            # Create a simple success popup
            popup = ctk.CTkToplevel(self.root)
            popup.title("Success!")
            popup.geometry("400x300")
            popup.resizable(False, False)
            
            # Center on parent
            popup.transient(self.root)
            popup.grab_set()
            
            x = self.root.winfo_rootx() + (self.root.winfo_width() - 400) // 2
            y = self.root.winfo_rooty() + (self.root.winfo_height() - 300) // 2
            popup.geometry(f"400x300+{x}+{y}")
            
            # Content
            success_icon = ctk.CTkLabel(popup, text="✨", font=ctk.CTkFont(size=48))
            success_icon.grid(row=0, column=0, pady=20)
            
            title_label = ctk.CTkLabel(popup, text=title, font=ctk.CTkFont(size=16, weight="bold"))
            title_label.grid(row=1, column=0, pady=(0, 10))
            
            message_label = ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=12),
                                       wraplength=350, justify="center")
            message_label.grid(row=2, column=0, pady=(0, 20))
            
            ok_btn = ctk.CTkButton(popup, text="Awesome! 🎉", command=popup.destroy,
                                 fg_color=("green", "darkgreen"))
            ok_btn.grid(row=3, column=0, pady=10)
            
            # Auto-close after 4 seconds
            popup.after(4000, popup.destroy)
            
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def add_ai_tooltip(self, button, task_data):
        """Add informative tooltip to AI button"""
        try:
            from .ai_button_tooltip import add_ai_button_tooltip
            add_ai_button_tooltip(button, task_data)
        except Exception as e:
            print(f"Error adding AI tooltip: {e}")
    
    def check_ai_status_background(self):
        """Check AI status in background and update indicator"""
        def check_status():
            try:
                response = requests.get(f"{self.api_base_url}/ai-agent/status", timeout=300)
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get("status", "unknown")
                    self.safe_ui_update(lambda: self.update_ai_status_indicator(status, status_data))
                else:
                    self.safe_ui_update(lambda: self.update_ai_status_indicator("offline", {}))
            except Exception:
                self.safe_ui_update(lambda: self.update_ai_status_indicator("offline", {}))
        
        # Check status in background
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()
    
    def update_ai_status_indicator(self, status, status_data):
        """Update the AI status indicator button"""
        if hasattr(self, 'ai_status_btn') and self.ai_status_btn.winfo_exists():
            try:
                if status == "online":
                    self.ai_status_btn.configure(
                        fg_color=("green", "darkgreen"),
                        hover_color=("darkgreen", "green"),
                        text="🤖✓"
                    )
                    tools_count = status_data.get("tools_available", 0)
                    self.ai_status_tooltip = f"AI Assistant Online\n{tools_count} tools available"
                elif status == "degraded":
                    self.ai_status_btn.configure(
                        fg_color=("orange", "darkorange"),
                        hover_color=("darkorange", "orange"),
                        text="🤖⚠"
                    )
                    self.ai_status_tooltip = "AI Assistant Degraded\nSome features may not work"
                else:
                    self.ai_status_btn.configure(
                        fg_color=("red", "darkred"),
                        hover_color=("darkred", "red"),
                        text="🤖✗"
                    )
                    self.ai_status_tooltip = "AI Assistant Offline\nCheck backend connection"
            except Exception as e:
                print(f"Error updating AI status indicator: {e}")
    
    def check_ai_status(self):
        """Show AI status when button is clicked"""
        if hasattr(self, 'ai_status_tooltip'):
            self.status_label.configure(text=self.ai_status_tooltip.replace('\n', ' - '))
            self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
        else:
            self.status_label.configure(text="Checking AI status...")
            self.check_ai_status_background()
    
    def run(self):
        """Start the main window"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run() 
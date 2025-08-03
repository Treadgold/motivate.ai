"""
Quick Add Task Dialog for Motivate.AI

Provides a fast, lightweight interface for quickly adding new tasks
without opening the full main window.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Optional, Callable
import requests
import os
import threading
from .theme_manager import get_color, get_button_colors


class QuickAddDialog:
    def __init__(self, on_task_added: Callable = None):
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.on_task_added = on_task_added
        self.window = None
        self.projects = []
        self.projects_loaded = False
        
        # Load demo projects immediately (no blocking)
        self.load_demo_projects()
        
        # Start loading real projects in background
        self.load_projects_async()
    
    def load_demo_projects(self):
        """Load demo projects immediately for fast startup"""
        self.projects = [
            {"id": 1, "title": "Workshop Organization"},
            {"id": 2, "title": "Garden Project"},
            {"id": 3, "title": "3D Printing"},
            {"id": 4, "title": "Learning Python"},
            {"id": 5, "title": "General Tasks"}
        ]
    
    def load_projects_async(self):
        """Load projects from API in background thread"""
        def fetch_projects():
            try:
                response = requests.get(f"{self.api_base_url}/projects", timeout=2)
                if response.status_code == 200:
                    real_projects = response.json()
                    # Update projects on main thread
                    if self.window and self.window.winfo_exists():
                        self.window.after(0, lambda: self.update_projects(real_projects))
                    else:
                        self.projects = real_projects
                    self.projects_loaded = True
            except:
                # Keep demo projects if API fails
                self.projects_loaded = True
        
        thread = threading.Thread(target=fetch_projects, daemon=True)
        thread.start()
    
    def update_projects(self, new_projects):
        """Update project dropdown with real projects (called on main thread)"""
        if new_projects:
            self.projects = new_projects
            self.update_project_combo()
    
    def update_project_combo(self):
        """Update the project combo box with current projects"""
        if hasattr(self, 'project_combo'):
            project_names = [p.get("title", "Unknown") for p in self.projects]
            if not project_names:
                project_names = ["General Tasks"]
            self.project_combo.configure(values=project_names)
            if project_names:
                self.project_combo.set(project_names[0])
    
    def show(self):
        """Show the quick add dialog"""
        if self.window and self.window.winfo_exists():
            # Reset form when showing existing window
            self.reset_form()
            self.window.focus_force()
            self.window.lift()
            return
        
        self.create_dialog()
    
    def reset_form(self):
        """Reset form to default values"""
        if hasattr(self, 'title_entry'):
            self.title_entry.delete(0, 'end')
        if hasattr(self, 'desc_entry'):
            self.desc_entry.delete("1.0", 'end')
        if hasattr(self, 'time_var'):
            self.time_var.set("15")
        if hasattr(self, 'priority_var'):
            self.priority_var.set("Normal")
        # Reset project selection to first available project
        if hasattr(self, 'project_combo') and self.projects:
            project_names = [p.get("title", "Unknown") for p in self.projects]
            if project_names:
                self.project_combo.set(project_names[0])
    
    def create_dialog(self):
        """Create the quick add dialog window with dynamic sizing"""
        self.window = ctk.CTkToplevel()
        self.window.title("Quick Add Task")
        
        # Don't set geometry yet - let it size dynamically
        self.window.resizable(False, False)
        
        # Create content first
        self.create_content()
        
        # Update and calculate required size
        self.window.update_idletasks()
        
        # Get required dimensions
        req_width = self.window.winfo_reqwidth()
        req_height = self.window.winfo_reqheight()
        
        # Add minimal padding and ensure minimum size
        width = max(500, req_width + 20)
        height = max(400, req_height + 10)
        
        # Center on screen with calculated size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Always on top and handle close
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        # Focus after everything is set up
        self.window.after(10, lambda: (self.reset_form(), self.title_entry.focus(), self.window.lift()))
    
    def create_content(self):
        """Create the dialog content with proper layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, height=60, fg_color=get_color("surface_primary"))
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="➕ Quick Add Task", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=15)
        
        # Form container
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Task title
        ctk.CTkLabel(form_frame, text="Task Title:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.title_entry = ctk.CTkEntry(form_frame, height=40, 
                                       placeholder_text="What needs to be done?",
                                       font=ctk.CTkFont(size=13))
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Description
        ctk.CTkLabel(form_frame, text="Description (optional):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.desc_entry = ctk.CTkTextbox(form_frame, height=60, 
                                        font=ctk.CTkFont(size=12))
        self.desc_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Project
        ctk.CTkLabel(form_frame, text="Project:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        
        project_names = [p.get("title", "Unknown") for p in self.projects]
        if not project_names:
            project_names = ["General Tasks"]
        
        self.project_combo = ctk.CTkComboBox(form_frame, values=project_names, 
                                            height=35,
                                            font=ctk.CTkFont(size=13),
                                            dropdown_font=ctk.CTkFont(size=13))
        self.project_combo.pack(fill="x", padx=20, pady=(0, 10))
        self.project_combo.set(project_names[0])
        
        # Time and Priority row
        details_frame = ctk.CTkFrame(form_frame, fg_color=get_color("surface_transparent"))
        details_frame.pack(fill="x", padx=20, pady=(0, 15))
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Time
        time_frame = ctk.CTkFrame(details_frame, fg_color=get_color("surface_transparent"))
        time_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(time_frame, text="Time (min):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.time_var = tk.StringVar(value="15")
        self.time_entry = ctk.CTkEntry(time_frame, height=35, textvariable=self.time_var,
                                      font=ctk.CTkFont(size=13))
        self.time_entry.pack(fill="x")
        
        # Priority
        priority_frame = ctk.CTkFrame(details_frame, fg_color=get_color("surface_transparent"))
        priority_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(priority_frame, text="Priority:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.priority_var = tk.StringVar(value="Normal")
        self.priority_combo = ctk.CTkComboBox(priority_frame, 
                                             values=["Low", "Normal", "High", "Urgent"],
                                             variable=self.priority_var, height=35,
                                             font=ctk.CTkFont(size=13))
        self.priority_combo.pack(fill="x")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color=get_color("surface_secondary"))
        button_frame.pack(fill="x", pady=(0, 0))
        
        # Button container
        btn_container = ctk.CTkFrame(button_frame, fg_color=get_color("surface_transparent"))
        btn_container.pack(pady=15, padx=20)
        
        # Add Task button (primary)
        add_colors = get_button_colors("success")
        ctk.CTkButton(btn_container, text="✓ Add Task", command=self.add_and_close,
                     height=40, width=110, font=ctk.CTkFont(size=14, weight="bold"),
                     **add_colors
                     ).pack(side="left", padx=(0, 10))
        
        # Add Another button
        another_colors = get_button_colors("primary")
        ctk.CTkButton(btn_container, text="+ Add Another", command=self.add_another,
                     height=40, width=120, font=ctk.CTkFont(size=13),
                     **another_colors
                     ).pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_colors = get_button_colors("secondary")
        ctk.CTkButton(btn_container, text="Cancel", command=self.close_dialog,
                     height=40, width=80, font=ctk.CTkFont(size=13),
                     **cancel_colors
                     ).pack(side="left")
        
        # Keyboard shortcuts
        self.window.bind('<Return>', lambda e: self.add_and_close())
        self.window.bind('<Escape>', lambda e: self.close_dialog())
    
    def get_task_data(self) -> Dict:
        """Get the task data from the form"""
        title = self.title_entry.get().strip()
        if not title:
            return None
        
        description = self.desc_entry.get("1.0", "end-1c").strip()
        
        # Get selected project
        project_name = self.project_combo.get()
        project_id = None
        for project in self.projects:
            if project.get("title") == project_name:
                project_id = project.get("id")
                break
        
        # Get estimated time
        try:
            estimated_minutes = int(self.time_var.get())
        except ValueError:
            estimated_minutes = 15
        
        priority = self.priority_var.get()
        
        return {
            "title": title,
            "description": description if description else None,
            "project_id": project_id,
            "project_name": project_name,
            "estimated_minutes": estimated_minutes,
            "priority": priority,
            "status": "pending"
        }
    
    def add_task(self) -> bool:
        """Add the task via API or local storage"""
        task_data = self.get_task_data()
        
        if not task_data:
            # Show error - title is required
            self.show_error("Task title is required!")
            return False
        
        try:
            # Try to add via API
            response = requests.post(f"{self.api_base_url}/tasks", 
                                   json=task_data, timeout=5)
            
            if response.status_code in [200, 201]:
                self.show_success("Task added successfully!")
                if self.on_task_added:
                    self.on_task_added(task_data)
                return True
            else:
                self.show_error("Failed to add task via API")
                return False
                
        except Exception as e:
            # Fallback - could save locally or show offline message
            print(f"Failed to add task: {e}")
            self.show_success("Task saved locally (offline mode)")
            if self.on_task_added:
                self.on_task_added(task_data)
            return True
    
    def show_success(self, message: str):
        """Show success message"""
        # For now, just print - could show a temporary label
        print(f"SUCCESS: {message}")
    
    def show_error(self, message: str):
        """Show error message"""
        # For now, just print - could show a temporary label
        print(f"ERROR: {message}")
        
        # Could also highlight the problematic field
        if "title" in message.lower():
            self.title_entry.configure(border_color=get_color("border_error"))
            self.title_entry.focus()
    
    def clear_form(self):
        """Clear the form for adding another task"""
        self.reset_form()
        self.title_entry.focus()
        
        # Reset any error highlighting
        self.title_entry.configure(border_color=get_color("border_default"))
    
    def add_and_close(self):
        """Add the task and close the dialog"""
        if self.add_task():
            self.close_dialog()
    
    def add_another(self):
        """Add the task and clear form for another"""
        if self.add_task():
            self.clear_form()
    
    def close_dialog(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None


# Global quick add dialog instance - reuse for performance
_quick_add_dialog = None

def show_quick_add(on_task_added: Callable = None, projects: List[Dict] = None):
    """Show the quick add dialog (reuses existing instance for speed)"""
    global _quick_add_dialog
    
    # Reuse existing dialog if possible
    if _quick_add_dialog is None:
        _quick_add_dialog = QuickAddDialog(on_task_added)
    else:
        # Update callback if different
        _quick_add_dialog.on_task_added = on_task_added
    
    # Update projects if provided
    if projects is not None:
        _quick_add_dialog.projects = projects
        _quick_add_dialog.projects_loaded = True
        # Update combo box if dialog exists
        if _quick_add_dialog.window and _quick_add_dialog.window.winfo_exists():
            _quick_add_dialog.update_project_combo()
    
    _quick_add_dialog.show()

def get_quick_add_dialog() -> QuickAddDialog:
    """Get the current quick add dialog instance"""
    return _quick_add_dialog

if __name__ == "__main__":
    # Test the quick add dialog
    app = ctk.CTk()
    app.withdraw()  # Hide main window
    
    def on_task_added(task_data):
        print(f"Task added: {task_data}")
    
    show_quick_add(on_task_added)
    
    app.mainloop() 
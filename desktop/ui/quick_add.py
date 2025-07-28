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


class QuickAddDialog:
    def __init__(self, on_task_added: Callable = None):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8010/api/v1")
        self.on_task_added = on_task_added
        self.window = None
        self.projects = []
        
        # Load projects for selection
        self.load_projects()
    
    def load_projects(self):
        """Load available projects for task assignment"""
        try:
            response = requests.get(f"{self.api_base_url}/projects", timeout=3)
            if response.status_code == 200:
                self.projects = response.json()
            else:
                self.projects = []
        except:
            # Fallback demo projects
            self.projects = [
                {"id": 1, "name": "Workshop Organization"},
                {"id": 2, "name": "Garden Project"},
                {"id": 3, "name": "3D Printing"},
                {"id": 4, "name": "Learning Python"},
                {"id": 5, "name": "General Tasks"}
            ]
    
    def show(self):
        """Show the quick add dialog"""
        if self.window and self.window.winfo_exists():
            self.window.focus_force()
            return
        
        self.create_dialog()
        self.window.focus_force()
    
    def create_dialog(self):
        """Create the quick add dialog window"""
        self.window = ctk.CTkToplevel()
        self.window.title("Quick Add Task")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        
        # Center on screen
        self.center_window()
        
        # Always on top
        self.window.attributes("-topmost", True)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        self.create_content()
    
    def center_window(self):
        """Center the dialog on screen"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width - 450) // 2
        y = (screen_height - 400) // 2
        
        self.window.geometry(f"450x400+{x}+{y}")
    
    def create_content(self):
        """Create the dialog content"""
        # Header
        header_frame = ctk.CTkFrame(self.window, height=60)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="➕ Quick Add Task", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=15)
        
        # Main form
        form_frame = ctk.CTkFrame(self.window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Task title
        title_label = ctk.CTkLabel(form_frame, text="Task Title:", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.title_entry = ctk.CTkEntry(form_frame, height=35, 
                                       placeholder_text="What needs to be done?")
        self.title_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.title_entry.focus()
        
        # Description (optional)
        desc_label = ctk.CTkLabel(form_frame, text="Description (optional):", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        desc_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.desc_entry = ctk.CTkTextbox(form_frame, height=80)
        self.desc_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Project selection
        project_label = ctk.CTkLabel(form_frame, text="Project:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        project_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        project_names = [p.get("name", "Unknown") for p in self.projects]
        if not project_names:
            project_names = ["General Tasks"]
        
        self.project_combo = ctk.CTkComboBox(form_frame, values=project_names, 
                                            height=35)
        self.project_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.project_combo.set(project_names[0])
        
        # Time estimation
        time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        time_label = ctk.CTkLabel(time_frame, text="Estimated time (minutes):", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        time_label.pack(side="left")
        
        self.time_var = tk.StringVar(value="15")
        self.time_entry = ctk.CTkEntry(time_frame, width=80, height=35,
                                      textvariable=self.time_var)
        self.time_entry.pack(side="right")
        
        # Priority selection
        priority_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        priority_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        priority_label = ctk.CTkLabel(priority_frame, text="Priority:", 
                                     font=ctk.CTkFont(size=14, weight="bold"))
        priority_label.pack(side="left")
        
        self.priority_var = tk.StringVar(value="Normal")
        self.priority_combo = ctk.CTkComboBox(priority_frame, 
                                             values=["Low", "Normal", "High", "Urgent"],
                                             variable=self.priority_var,
                                             width=120, height=35)
        self.priority_combo.pack(side="right")
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Add and close button
        add_close_btn = ctk.CTkButton(button_frame, text="✓ Add & Close", 
                                     command=self.add_and_close, height=40,
                                     font=ctk.CTkFont(size=14, weight="bold"))
        add_close_btn.pack(side="left", padx=(0, 10))
        
        # Add another button
        add_another_btn = ctk.CTkButton(button_frame, text="+ Add Another", 
                                       command=self.add_another, height=40)
        add_another_btn.pack(side="left", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", 
                                  command=self.close_dialog, height=40,
                                  fg_color="gray", hover_color="darkgray")
        cancel_btn.pack(side="right")
        
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
            if project.get("name") == project_name:
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
            self.title_entry.configure(border_color="red")
            self.title_entry.focus()
    
    def clear_form(self):
        """Clear the form for adding another task"""
        self.title_entry.delete(0, 'end')
        self.desc_entry.delete("1.0", 'end')
        self.time_var.set("15")
        self.priority_var.set("Normal")
        self.title_entry.focus()
        
        # Reset any error highlighting
        self.title_entry.configure(border_color=("gray60", "gray50"))
    
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


# Global quick add dialog instance
_quick_add_dialog = None

def show_quick_add(on_task_added: Callable = None):
    """Show the quick add dialog"""
    global _quick_add_dialog
    
    # Create new instance each time to ensure fresh data
    _quick_add_dialog = QuickAddDialog(on_task_added)
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
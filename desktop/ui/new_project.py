"""
New Project Dialog for Motivate.AI Desktop App

Creates a dialog for adding new projects with all the necessary fields
matching the backend API schema.
"""

import os
import requests
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional, Dict, Any


class NewProjectDialog:
    """Dialog for creating new projects"""
    
    def __init__(self, parent=None, on_project_created: Optional[Callable] = None):
        self.parent = parent
        self.on_project_created = on_project_created
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        
        # Dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("New Project")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.center_dialog()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Form variables
        self.title_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.priority_var = ctk.StringVar(value="medium")
        self.estimated_time_var = ctk.StringVar()
        self.tags_var = ctk.StringVar()
        self.location_var = ctk.StringVar()
        self.next_action_var = ctk.StringVar()
        
        # Create the UI
        self.create_ui()
        
        # Focus on title field
        self.title_entry.focus()
    
    def center_dialog(self):
        """Center the dialog on the parent window or screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            x = (self.dialog.winfo_screenwidth() - width) // 2
            y = (self.dialog.winfo_screenheight() - height) // 2
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_ui(self):
        """Create the dialog UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame, 
            text="Create New Project", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header_label.pack(pady=(10, 20))
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_form_fields(self, parent):
        """Create the form input fields"""
        
        # Title (required)
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ctk.CTkLabel(title_frame, text="Project Title *", 
                                  font=ctk.CTkFont(weight="bold"))
        title_label.pack(anchor="w")
        
        self.title_entry = ctk.CTkEntry(
            title_frame, 
            textvariable=self.title_var,
            placeholder_text="Enter project title...",
            height=40
        )
        self.title_entry.pack(fill="x", pady=(5, 0))
        
        # Description
        desc_frame = ctk.CTkFrame(parent, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(0, 15))
        
        desc_label = ctk.CTkLabel(desc_frame, text="Description", 
                                 font=ctk.CTkFont(weight="bold"))
        desc_label.pack(anchor="w")
        
        self.description_textbox = ctk.CTkTextbox(
            desc_frame,
            height=80,
            wrap="word"
        )
        self.description_textbox.pack(fill="x", pady=(5, 0))
        
        # Priority and Estimated Time (side by side)
        priority_time_frame = ctk.CTkFrame(parent, fg_color="transparent")
        priority_time_frame.pack(fill="x", pady=(0, 15))
        priority_time_frame.grid_columnconfigure(0, weight=1)
        priority_time_frame.grid_columnconfigure(1, weight=1)
        
        # Priority
        priority_frame = ctk.CTkFrame(priority_time_frame, fg_color="transparent")
        priority_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        priority_label = ctk.CTkLabel(priority_frame, text="Priority", 
                                     font=ctk.CTkFont(weight="bold"))
        priority_label.pack(anchor="w")
        
        self.priority_combo = ctk.CTkComboBox(
            priority_frame,
            values=["low", "medium", "high", "urgent"],
            variable=self.priority_var,
            height=35
        )
        self.priority_combo.pack(fill="x", pady=(5, 0))
        
        # Estimated Time
        time_frame = ctk.CTkFrame(priority_time_frame, fg_color="transparent")
        time_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        time_label = ctk.CTkLabel(time_frame, text="Estimated Time (hours)", 
                                 font=ctk.CTkFont(weight="bold"))
        time_label.pack(anchor="w")
        
        self.time_entry = ctk.CTkEntry(
            time_frame,
            textvariable=self.estimated_time_var,
            placeholder_text="e.g., 2.5",
            height=35
        )
        self.time_entry.pack(fill="x", pady=(5, 0))
        
        # Tags
        tags_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(0, 15))
        
        tags_label = ctk.CTkLabel(tags_frame, text="Tags (comma-separated)", 
                                 font=ctk.CTkFont(weight="bold"))
        tags_label.pack(anchor="w")
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            textvariable=self.tags_var,
            placeholder_text="e.g., personal, creative, urgent",
            height=35
        )
        self.tags_entry.pack(fill="x", pady=(5, 0))
        
        # Location
        location_frame = ctk.CTkFrame(parent, fg_color="transparent")
        location_frame.pack(fill="x", pady=(0, 15))
        
        location_label = ctk.CTkLabel(location_frame, text="Location", 
                                     font=ctk.CTkFont(weight="bold"))
        location_label.pack(anchor="w")
        
        self.location_entry = ctk.CTkEntry(
            location_frame,
            textvariable=self.location_var,
            placeholder_text="e.g., home office, garage, garden",
            height=35
        )
        self.location_entry.pack(fill="x", pady=(5, 0))
        
        # Next Action
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 15))
        
        action_label = ctk.CTkLabel(action_frame, text="Next Action", 
                                   font=ctk.CTkFont(weight="bold"))
        action_label.pack(anchor="w")
        
        self.action_entry = ctk.CTkEntry(
            action_frame,
            textvariable=self.next_action_var,
            placeholder_text="What's the first thing to do?",
            height=35
        )
        self.action_entry.pack(fill="x", pady=(5, 0))
    
    def create_buttons(self, parent):
        """Create the action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 10))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Create button
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create Project",
            width=140,
            height=40,
            command=self.create_project
        )
        create_btn.pack(side="right")
        
        # Required field note
        note_label = ctk.CTkLabel(
            button_frame,
            text="* Required field",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        note_label.pack(side="left")
    
    def validate_form(self) -> bool:
        """Validate the form data"""
        # Check required fields
        if not self.title_var.get().strip():
            messagebox.showerror("Validation Error", "Project title is required!")
            self.title_entry.focus()
            return False
        
        # Validate estimated time if provided
        if self.estimated_time_var.get().strip():
            try:
                float(self.estimated_time_var.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Estimated time must be a number!")
                self.time_entry.focus()
                return False
        
        return True
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get the form data as a dictionary for the API"""
        data = {
            "title": self.title_var.get().strip(),
            "priority": self.priority_var.get()
        }
        
        # Add optional fields if they have values
        description = self.description_textbox.get("1.0", "end-1c").strip()
        if description:
            data["description"] = description
        
        if self.estimated_time_var.get().strip():
            data["estimated_time"] = int(float(self.estimated_time_var.get()) * 60)  # Convert to minutes
        
        if self.tags_var.get().strip():
            data["tags"] = self.tags_var.get().strip()
        
        if self.location_var.get().strip():
            data["location"] = self.location_var.get().strip()
        
        if self.next_action_var.get().strip():
            data["next_action"] = self.next_action_var.get().strip()
        
        return data
    
    def create_project(self):
        """Create the project via API call"""
        if not self.validate_form():
            return
        
        try:
            # Get form data
            project_data = self.get_form_data()
            
            # Make API call
            response = requests.post(
                f"{self.api_base_url}/projects",
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 200:
                created_project = response.json()
                messagebox.showinfo("Success", f"Project '{created_project['title']}' created successfully!")
                
                # Call callback if provided
                if self.on_project_created:
                    self.on_project_created(created_project)
                
                # Close dialog
                self.dialog.destroy()
                
            else:
                messagebox.showerror("Error", f"Failed to create project: {response.text}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                "Connection Error", 
                "Could not connect to the backend. Please ensure the backend is running."
            )
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout Error", "Request timed out. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def cancel(self):
        """Cancel and close the dialog"""
        self.dialog.destroy()


def show_new_project_dialog(parent=None, on_project_created: Optional[Callable] = None):
    """Show the new project dialog"""
    return NewProjectDialog(parent, on_project_created) 
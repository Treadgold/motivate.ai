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
from .theme_manager import get_color, get_button_colors, register_theme_change_callback, ThemeMode, apply_theme_change

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
        
        # Cache frequently used colors for performance
        self.color_cache = self._build_color_cache()
        
        # Register for theme changes
        register_theme_change_callback(self._on_theme_changed)
        
        # Create main window FIRST - required for font creation
        self.root = ctk.CTk()
        self.root.title("Motivate.AI")
        self.root.geometry("1450x900")
        self.root.minsize(800, 600)
        
        # Cache fonts for performance AFTER root window is created
        self.font_cache = self._build_font_cache()
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_rowconfigure(1, weight=2)
        
        # Setup UI immediately (non-blocking)
        self.setup_ui()
        
        # Bind window resize event for dynamic text wrapping
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Load projects immediately (no async needed since window shows instantly)
        self.load_projects_data()
    
    def _build_color_cache(self):
        """Build cache of frequently used colors for performance"""
        return {
            'task_card_hover': get_color("task_card_hover"),
            'task_card_normal': get_color("task_card_normal"),
            'card_hover': get_color("card_hover"),
            'card_normal': get_color("card_normal"),
            'surface_transparent': get_color("surface_transparent"),
            'text_primary': get_color("text_primary"),
            'text_secondary': get_color("text_secondary"),
            'text_tertiary': get_color("text_tertiary"),
            'text_muted': get_color("text_muted"),
            'surface_primary': get_color("surface_primary"),
            'surface_secondary': get_color("surface_secondary"),
            'success': get_color("success"),
            'primary': get_color("primary"),
            'danger': get_color("danger"),
            'danger_hover': get_color("danger_hover"),
            'progress_bg': get_color("progress_bg"),
            'success_light': get_color("success_light"),
            'warning': get_color("warning"),
            'border_default': get_color("border_default"),
            'border_error': get_color("border_error")
        }
    
    def get_cached_color(self, color_key):
        """Get color from cache or fallback to get_color()"""
        return self.color_cache.get(color_key, get_color(color_key))
    
    def refresh_color_cache(self):
        """Refresh color cache when theme changes"""
        self.color_cache = self._build_color_cache()
    
    def _build_font_cache(self):
        """Build cache of frequently used fonts - MAJOR PERFORMANCE IMPROVEMENT"""
        return {
            # Task fonts
            'task_title_bold': ctk.CTkFont(size=14, weight="bold"),
            'task_title_normal': ctk.CTkFont(size=14, weight="normal"),
            'task_description': ctk.CTkFont(size=11),
            'task_details': ctk.CTkFont(size=10),
            
            # Button fonts
            'button_small': ctk.CTkFont(size=11),
            'button_medium': ctk.CTkFont(size=12),
            'button_large': ctk.CTkFont(size=13),
            'button_bold': ctk.CTkFont(size=11, weight="bold"),
            
            # Header fonts
            'header_large': ctk.CTkFont(size=24, weight="bold"),
            'header_medium': ctk.CTkFont(size=20, weight="bold"),
            'header_small': ctk.CTkFont(size=16, weight="bold"),
            'header_normal': ctk.CTkFont(size=18, weight="bold"),
            
            # UI element fonts
            'toolbar_button': ctk.CTkFont(size=18),
            'toolbar_large': ctk.CTkFont(size=20),
            'label_normal': ctk.CTkFont(size=13),
            'label_small': ctk.CTkFont(size=12),
            'status': ctk.CTkFont(size=12),
            
            # Project fonts
            'project_title': ctk.CTkFont(size=14, weight="bold"),
            'project_stats': ctk.CTkFont(size=11),
            'project_percentage': ctk.CTkFont(size=10, weight="bold"),
            
            # Form fonts
            'form_entry': ctk.CTkFont(size=13),
            'form_label': ctk.CTkFont(size=14, weight="bold"),
        }
    
    def get_cached_font(self, font_key):
        """Get font from cache - prevents creating new font objects"""
        # Ensure font cache exists
        if not hasattr(self, 'font_cache') or not self.font_cache:
            return ctk.CTkFont(size=12)  # Safe fallback
        return self.font_cache.get(font_key, ctk.CTkFont(size=12))  # Fallback
    
    def load_and_apply_settings(self):
        """Load and apply settings from file"""
        try:
            from .settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(None)  # No parent needed for loading
            
            # Apply appearance settings through theme manager
            theme = settings_dialog.settings["appearance"]["theme"]
            if theme == "light":
                apply_theme_change(ThemeMode.LIGHT)
            elif theme == "dark":
                apply_theme_change(ThemeMode.DARK)
            else:
                apply_theme_change(ThemeMode.SYSTEM)
            
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
    
    def _on_theme_changed(self):
        """Handle theme changes - update window colors"""
        if self.root and self.root.winfo_exists():
            # Refresh color cache for new theme
            self.refresh_color_cache()
            # Force a refresh of the current project tasks to update colors
            if hasattr(self, 'selected_project_id') and self.selected_project_id:
                self.load_tasks_list(self.selected_project_id)
    
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
        """Process pending UI updates with throttling to prevent blocking"""
        # Process maximum 5 updates at a time to prevent UI blocking
        max_updates_per_cycle = 5
        processed = 0
        
        while self.pending_updates and processed < max_updates_per_cycle:
            try:
                callback = self.pending_updates.pop(0)
                callback()
                processed += 1
            except Exception as e:
                print(f"Error processing pending update: {e}")
                processed += 1
        
        # If more updates remain, schedule them for next cycle
        if self.pending_updates:
            self.root.after(10, self.process_pending_updates)
    
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
        title_frame = ctk.CTkFrame(toolbar_frame, fg_color=get_color("surface_transparent"))
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        menu_btn = ctk.CTkButton(title_frame, text="≡", width=40, height=40, 
                                command=self.toggle_sidebar, font=self.get_cached_font('toolbar_large'))
        menu_btn.grid(row=0, column=0, padx=(0, 10))
        
        title_label = ctk.CTkLabel(title_frame, text="Motivate.AI", 
                                  font=self.get_cached_font('header_large'))
        title_label.grid(row=0, column=1)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(toolbar_frame, fg_color=get_color("surface_transparent"))
        actions_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        
        # Speech button
        self.speech_btn = ctk.CTkButton(actions_frame, text="🎤", width=40, height=40,
                                       command=self.voice_input, font=self.get_cached_font('toolbar_button'))
        self.speech_btn.grid(row=0, column=0, padx=2)
        
        # Search button
        search_btn = ctk.CTkButton(actions_frame, text="🔍", width=40, height=40,
                                  command=self.toggle_search, font=self.get_cached_font('toolbar_button'))
        search_btn.grid(row=0, column=1, padx=2)
        
        # Quick add button - Now functional!
        add_btn = ctk.CTkButton(actions_frame, text="➕", width=40, height=40,
                               command=self.quick_add_task, font=self.get_cached_font('toolbar_button'))
        add_btn.grid(row=0, column=2, padx=2)
        
        # AI Status indicator
        ai_status_colors = get_button_colors("secondary")
        self.ai_status_btn = ctk.CTkButton(actions_frame, text="🤖", width=40, height=40,
                                          command=self.check_ai_status,
                                          font=self.get_cached_font('toolbar_button'),
                                          **ai_status_colors)
        self.ai_status_btn.grid(row=0, column=3, padx=2)
        
        # Settings button
        settings_btn = ctk.CTkButton(actions_frame, text="⚙️", width=40, height=40,
                                    command=self.open_settings, font=self.get_cached_font('toolbar_button'))
        settings_btn.grid(row=0, column=4, padx=2)
        
        # Check AI status after main loop starts
        self.root.after(1000, self.check_ai_status_background)
    
    def create_main_content(self):
        """Create the main content area with resizable sidebar, task view, and task detail pane"""
        
        # Create a main container for the paned window with reduced padding
        main_container = ctk.CTkFrame(self.root)
        main_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=3)  # Reduced padding
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
        
        # Add all three panels to the paned window with optimized sizing
        self.paned_window.add(self.sidebar_frame, minsize=350, width=580)  # Reduced minimum width
        self.paned_window.add(self.task_frame, minsize=450)  # Allow more flexible sizing
        self.paned_window.add(self.task_detail_frame, minsize=400, width=420)  # Reduced width
        
        self.sidebar_visible = True
        self.task_detail_visible = True
        self.selected_task = None
        self.editing_task = False
    
    def create_sidebar(self):
        """Create the projects sidebar (without loading data)"""
        self.sidebar_frame = ctk.CTkFrame(self.paned_window)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)  # Allow sidebar to expand horizontally
        
        # Sidebar header with reduced padding
        sidebar_header = ctk.CTkLabel(self.sidebar_frame, text="Projects", 
                                     font=self.get_cached_font('header_small'))  # Use cached font
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=10, pady=8)  # Reduced padding
        
        # Projects list (scrollable) with reduced padding
        self.projects_frame = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.projects_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))  # Reduced padding
        self.projects_frame.grid_columnconfigure(0, weight=1)  # Allow projects frame to expand
        
        # Add project button with reduced size and padding
        add_project_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Project",
                                       command=self.add_project, height=32,
                                       font=self.get_cached_font('label_small'))  # Use cached font
        add_project_btn.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))  # Reduced padding

    def create_task_view(self):
        """Create the main task view area"""
        self.task_frame = ctk.CTkFrame(self.paned_window)
        self.task_frame.grid_rowconfigure(1, weight=1)
        self.task_frame.grid_columnconfigure(0, weight=1)  # Allow task frame to expand horizontally
        
        # Task view header with filters
        self.create_task_header()
        
        # Main task list area with reduced padding
        self.task_list_frame = ctk.CTkScrollableFrame(self.task_frame)
        self.task_list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))  # Reduced padding
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
                                            font=self.get_cached_font('header_normal'))
        self.task_detail_title.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color=get_color("surface_transparent"))
        button_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)
        
        # Save button
        save_colors = get_button_colors("success")
        self.save_btn = ctk.CTkButton(button_frame, text="💾 Save", width=80, height=35,
                                     command=self.save_task,
                                     **save_colors)
        self.save_btn.grid(row=0, column=0, padx=2)
        
        # Cancel/Clear button
        cancel_colors = get_button_colors("secondary")
        self.cancel_btn = ctk.CTkButton(button_frame, text="✖ Clear", width=80, height=35,
                                       command=self.clear_task_form,
                                       **cancel_colors)
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
        
        # Description with dynamic markdown-style formatting
        ctk.CTkLabel(self.task_detail_content, text="Description:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Create the dynamic markdown description area
        self.create_markdown_description_area()
        
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
        details_frame = ctk.CTkFrame(self.task_detail_content, fg_color=get_color("surface_transparent"))
        details_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=(0, 15))
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Time
        time_frame = ctk.CTkFrame(details_frame, fg_color=get_color("surface_transparent"))
        time_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        time_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(time_frame, text="Time (min):", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.time_var = tk.StringVar(value="15")
        self.time_entry = ctk.CTkEntry(time_frame, height=35, textvariable=self.time_var,
                                      font=ctk.CTkFont(size=13))
        self.time_entry.grid(row=1, column=0, sticky="ew")
        
        # Priority
        priority_frame = ctk.CTkFrame(details_frame, fg_color=get_color("surface_transparent"))
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
        self.status_frame = ctk.CTkFrame(self.task_detail_content, fg_color=get_color("surface_transparent"))
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
        self.set_description_text("")  # This will show placeholder text
        self.time_var.set("15")
        self.priority_var.set("Normal")
        self.status_var.set("pending")
        
        # Reset to new task mode
        self.editing_task = False
        self.selected_task = None
        self.task_detail_title.configure(text="➕ New Task")
        self.cancel_btn.configure(text="✖ Clear")
        
        # Clear selection highlighting
        self._update_task_selection_highlighting()
        
        # Hide status frame for new tasks
        self.status_frame.grid_remove()
        
        # Set project to currently selected if available
        if self.selected_project:
            self.project_combo.set(self.selected_project.get("title", "General Tasks"))
        
        # Focus on title
        self.title_entry.focus()
    
    def create_markdown_description_area(self):
        """Create a dynamic markdown-style description area"""
        # Container for the description area
        self.desc_container = ctk.CTkFrame(self.task_detail_content, fg_color="transparent")
        self.desc_container.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 15))
        self.desc_container.grid_columnconfigure(0, weight=1)
        
        # Create a single textbox that will serve as both display and edit
        self.desc_entry = ctk.CTkTextbox(self.desc_container, height=200, 
                                        wrap="word",
                                        border_width=1,
                                        corner_radius=8)
        self.desc_entry.grid(row=0, column=0, sticky="ew", pady=2)
        
        # Track if we're in edit mode
        self.desc_editing = False
        self._original_text = ""
        
        # Bind events for dynamic editing
        self.desc_entry.bind("<Button-1>", self.on_description_click)
        self.desc_entry.bind("<KeyPress>", self.on_description_keypress)
        self.desc_entry.bind("<FocusOut>", self.on_description_focus_out)
        
        # Start with placeholder
        self.set_description_placeholder()
    
    def set_description_placeholder(self):
        """Set placeholder text in description"""
        self.desc_entry.delete("1.0", tk.END)
        placeholder_text = "Click here to add a task description...\n\nTip: Use numbered lists (1. 2. 3.) and separate items with commas for automatic formatting."
        self.desc_entry.insert("1.0", placeholder_text)
        
        # Make placeholder text look different - better for dark mode
        self.desc_entry.tag_add("placeholder", "1.0", tk.END)
        self.desc_entry.tag_config("placeholder", 
                                  foreground="#808080")  # Medium gray for good contrast
        self.desc_editing = False
        self._original_text = ""
    
    def on_description_click(self, event):
        """Handle clicks on the description area"""
        if not self.desc_editing:
            self.enter_edit_mode()
    
    def on_description_keypress(self, event):
        """Handle key presses in description area"""
        if not self.desc_editing:
            self.enter_edit_mode()
    
    def enter_edit_mode(self):
        """Enter edit mode - clear formatting and show plain text"""
        self.desc_editing = True
        
        # If it's placeholder text, clear it
        if not self._original_text:
            self.desc_entry.delete("1.0", tk.END)
        else:
            # Load the original plain text for editing
            self.desc_entry.delete("1.0", tk.END)
            self.desc_entry.insert("1.0", self._original_text)
        
        # Remove all tags to show plain text
        for tag in self.desc_entry.tag_names():
            self.desc_entry.tag_delete(tag)
        
        # Configure for editing - focus without changing font
        self.desc_entry.focus()
    
    def on_description_focus_out(self, event):
        """Handle focus out - apply formatting if there's content"""
        if self.desc_editing:
            current_text = self.desc_entry.get("1.0", tk.END).strip()
            if current_text:
                self.apply_markdown_formatting(current_text)
                self._original_text = current_text
                self.desc_editing = False
            else:
                self.set_description_placeholder()
    
    def apply_markdown_formatting(self, text):
        """Apply beautiful markdown-style formatting to the text"""
        self.desc_entry.delete("1.0", tk.END)
        
        # Process the text with our formatting function
        formatted_text = self.format_for_detail_view(text)
        
        # Insert the formatted text
        self.desc_entry.insert("1.0", formatted_text)
        
        # Apply styling to different parts
        self.apply_text_styling()
    
    def apply_text_styling(self):
        """Apply clean, dark-mode friendly styling to the formatted content"""
        content = self.desc_entry.get("1.0", tk.END)
        lines = content.split('\n')
        
        # Clear existing tags
        for tag in self.desc_entry.tag_names():
            self.desc_entry.tag_delete(tag)
        
        current_line = 1
        for line in lines:
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end"
            
            if line.strip().startswith('💡'):
                # Style tip sections - bright blue for visibility
                self.desc_entry.tag_add("tip", line_start, line_end)
                self.desc_entry.tag_config("tip", 
                                          foreground="#4A9EFF")  # Bright blue
            
            elif line.strip().startswith('•'):
                # Style bullet points - light gray for good contrast
                self.desc_entry.tag_add("bullet", line_start, line_end)
                self.desc_entry.tag_config("bullet", 
                                          foreground="#B0B0B0",  # Light gray
                                          lmargin1=20, lmargin2=20)  # Smaller indent
            
            elif any(line.strip().startswith(f'{i}.') for i in range(1, 10)):
                # Style numbered sections - white for headers
                self.desc_entry.tag_add("section", line_start, line_end)
                self.desc_entry.tag_config("section", 
                                          foreground="#FFFFFF",  # White for dark mode
                                          spacing3=2)  # Small spacing after
            
            else:
                # Regular text styling - light color for readability
                self.desc_entry.tag_add("normal", line_start, line_end)
                self.desc_entry.tag_config("normal", 
                                          foreground="#E0E0E0")  # Light gray
            
            current_line += 1
    
    def get_description_text(self):
        """Get the current description text"""
        if self.desc_editing:
            return self.desc_entry.get("1.0", tk.END).strip()
        else:
            return self._original_text
    
    def set_description_text(self, text):
        """Set description text and apply formatting"""
        self._original_text = text
        
        if text and text.strip():
            self.apply_markdown_formatting(text)
            self.desc_editing = False
        else:
            self.set_description_placeholder()
    
    def save_task(self):
        """Save the current task (new or edited)"""
        # Get form data
        title = self.title_entry.get().strip()
        description = self.get_description_text()
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
            "estimated_minutes": int(time_minutes) if time_minutes.isdigit() else 15,
            "priority": priority.lower(),
            "status": status,
            "is_completed": status == "completed"
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
                    self.load_projects_list()  # Refresh project pane with updated statistics
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
                    self.load_projects_list()  # Refresh project pane with updated statistics
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
        
        # Update visual selection highlighting
        self._update_task_selection_highlighting()
        
        # Update header
        self.task_detail_title.configure(text="✏️ Edit Task")
        self.cancel_btn.configure(text="✖ Cancel")
        
        # Populate form fields
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, task.get("title", ""))
        
        # Set description using the new dual-mode interface
        original_description = task.get("description", "")
        self.set_description_text(original_description)
        
        # Set project
        project_title = "General Tasks"
        for project in self.projects:
            if project.get("id") == task.get("project_id"):
                project_title = project.get("title", "General Tasks")
                break
        self.project_combo.set(project_title)
        
        # Set time, priority, and status
        self.time_var.set(str(task.get("estimated_minutes", 15)))
        self.priority_var.set(task.get("priority", "normal").title())
        self.status_var.set(task.get("status", "pending"))
        
        # Show status field for editing
        self.status_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=(0, 15))
        
        # Focus on title for editing
        self.title_entry.focus()
    
    def _update_task_selection_highlighting(self):
        """Update visual highlighting for the selected task"""
        if not hasattr(self, '_task_frames'):
            self._task_frames = {}
            
        # Clear previous selection highlighting
        for task_frame in self._task_frames.values():
            if task_frame.winfo_exists():
                task_frame.configure(border_width=0)
        
        # Highlight selected task with subtle border
        if self.selected_task and self.selected_task.get("id") in self._task_frames:
            selected_frame = self._task_frames[self.selected_task.get("id")]
            if selected_frame.winfo_exists():
                # Subtle blue border for selection - much better than changing background color
                selected_frame.configure(border_width=2, border_color=self.get_cached_color("border_focus"))
    
    def create_task_header(self):
        """Create the task view header with filters and actions"""
        header_frame = ctk.CTkFrame(self.task_frame, height=45)  # Reduced height
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 3))  # Reduced padding
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Task filters with reduced padding
        filter_frame = ctk.CTkFrame(header_frame, fg_color=get_color("surface_transparent"))
        filter_frame.grid(row=0, column=0, sticky="w", padx=8, pady=6)  # Reduced padding
        
        # Filter buttons - smaller and more compact
        all_btn = ctk.CTkButton(filter_frame, text="All", width=55, height=26,
                               command=lambda: self.filter_tasks("all"),
                               font=self.get_cached_font('label_small'))
        all_btn.grid(row=0, column=0, padx=1)
        
        active_btn = ctk.CTkButton(filter_frame, text="Active", width=55, height=26,
                                  command=lambda: self.filter_tasks("active"),
                                  font=self.get_cached_font('label_small'))
        active_btn.grid(row=0, column=1, padx=1)
        
        completed_btn = ctk.CTkButton(filter_frame, text="Done", width=55, height=26,
                                     command=lambda: self.filter_tasks("completed"),
                                     font=self.get_cached_font('label_small'))
        completed_btn.grid(row=0, column=2, padx=1)
        
        # Task view title - shows selected project with reduced size
        self.task_title = ctk.CTkLabel(header_frame, text="Select a project to view tasks", 
                                      font=self.get_cached_font('header_small'))  # Use cached font
        self.task_title.grid(row=0, column=1, padx=15)  # Reduced padding
    
    def load_tasks_list(self, project_id=None):
        """Load and display tasks for the selected project"""
        # Clear existing tasks immediately
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        if project_id is None:
            # Show empty state
            empty_label = ctk.CTkLabel(self.task_list_frame, 
                                      text="Select a project from the sidebar to view its tasks",
                                      font=self.get_cached_font('header_small'),
                                      text_color=get_color("text_secondary"))
            empty_label.grid(pady=50)
            return

        # Show loading state immediately for instant feedback
        loading_label = ctk.CTkLabel(self.task_list_frame, 
                                    text="Loading tasks...",
                                    font=self.get_cached_font('header_small'),
                                    text_color="gray")
        loading_label.grid(pady=50)

        # Load real tasks from backend in background thread
        def load_tasks_async():
            try:
                print(f"DEBUG: Fetching tasks from API for project {project_id}")
                response = requests.get(f"{self.api_base_url}/tasks?project_id={project_id}", timeout=10)
                if response.status_code == 200:
                    real_tasks = response.json()
                    print(f"DEBUG: Loaded {len(real_tasks)} tasks from API")
                    
                    # Log first task's description for debugging
                    if real_tasks and len(real_tasks) > 0:
                        first_task = real_tasks[0]
                        desc = first_task.get('description', '')
                        print(f"DEBUG: First task '{first_task.get('title', 'N/A')}' description length: {len(desc)}")
                        print(f"DEBUG: First task description preview: {desc[:100]}...")
                    
                    # Update UI on main thread safely with real data
                    self.safe_ui_update(lambda: self.update_tasks_ui(real_tasks, project_id))
                else:
                    print(f"DEBUG: API returned status {response.status_code}")
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
                                  font=self.get_cached_font('header_small'),
                                  text_color="gray")
        empty_label.grid(pady=50)
    
    def show_offline_message(self):
        """Show message when backend is offline"""
        # Clear loading message
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        offline_label = ctk.CTkLabel(self.task_list_frame, 
                                    text="Cannot connect to backend.\nPlease check your connection and try again.",
                                    font=self.get_cached_font('header_small'),
                                    text_color="red")
        offline_label.grid(pady=50)
    
    def update_tasks_ui(self, tasks, project_id):
        """Update the tasks UI on the main thread with incremental updates when possible"""
        # Store new tasks
        new_tasks = tasks
        
        # Check if we can do incremental update
        if hasattr(self, 'tasks') and self.tasks and len(self.tasks) > 0:
            # Try incremental update if task counts are similar
            if abs(len(new_tasks) - len(self.tasks)) <= 3:  # Small change
                if self._try_incremental_update(new_tasks):
                    self.tasks = new_tasks
                    return
        
        # Fall back to full rebuild for major changes
        self._full_tasks_rebuild(new_tasks)
        
    def _try_incremental_update(self, new_tasks):
        """Try to update tasks incrementally - returns True if successful"""
        try:
            # Create lookup maps
            old_tasks = {task.get('id'): task for task in self.tasks if task.get('id')}
            new_tasks_map = {task.get('id'): task for task in new_tasks if task.get('id')}
            
            # Quick check - if task IDs don't mostly match, do full rebuild
            if len(set(old_tasks.keys()) & set(new_tasks_map.keys())) < len(old_tasks) * 0.7:
                return False
                
            # Update existing widgets in place where possible
            widgets = list(self.task_list_frame.winfo_children())
            for i, widget in enumerate(widgets):
                if i < len(new_tasks) and hasattr(widget, 'task_id'):
                    old_task_id = widget.task_id
                    new_task = new_tasks[i]
                    new_task_id = new_task.get('id')
                    
                    # If task ID matches, just update the data
                    if old_task_id == new_task_id:
                        old_task = old_tasks.get(old_task_id)
                        if old_task and self._task_needs_update(old_task, new_task):
                            self._update_task_widget(widget, new_task)
                    else:
                        # Different task, needs rebuild
                        return False
                else:
                    # Length mismatch or missing data
                    return False
            
            return True
            
        except Exception as e:
            print(f"Incremental update failed: {e}")
            return False
    
    def _task_needs_update(self, old_task, new_task):
        """Check if a task has changed and needs UI update"""
        check_fields = ['title', 'description', 'status', 'priority', 'estimated_minutes']
        for field in check_fields:
            if old_task.get(field) != new_task.get(field):
                return True
        return False
    
    def _update_task_widget(self, widget, task):
        """Update an existing task widget with new task data"""
        # This is complex to implement properly without major refactoring
        # For now, just mark for full rebuild
        return False
    
    def _full_tasks_rebuild(self, tasks):
        """Full rebuild of the tasks UI"""
        # Clear loading message and existing widgets
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # Clear task frame references for highlighting
        if hasattr(self, '_task_frames'):
            self._task_frames.clear()

        # Store tasks
        self.tasks = tasks

        # Create task items
        if self.tasks:
            for i, task in enumerate(self.tasks):
                task_widget = self.create_task_item(task)
                # Store task ID for incremental updates
                if task_widget and task.get('id'):
                    task_widget.task_id = task.get('id')
            
            # Update text wrapping after all tasks are created to ensure proper sizing
            self.root.after(100, self.update_text_wrapping)
        else:
            empty_label = ctk.CTkLabel(self.task_list_frame, 
                                      text="No tasks in this project yet.\nClick the ➕ button to add some!",
                                      font=self.get_cached_font('header_small'),
                                      text_color="gray")
            empty_label.grid(pady=50)
    
    def create_task_item(self, task):
        """Create a clickable task item in the task list with AI split button"""
        # Create task frame without fixed height - let it expand based on content
        task_frame = ctk.CTkFrame(self.task_list_frame)
        task_frame.grid(sticky="ew", padx=3, pady=1)  # Allow horizontal expansion
        task_frame.grid_columnconfigure(1, weight=1)  # Content expands fully
        task_frame.grid_rowconfigure(0, weight=1)  # Allow vertical expansion
        
        # Store task data on frame to avoid lambda overhead
        task_frame.task_data = task
        
        # Store frame reference for selection highlighting
        if not hasattr(self, '_task_frames'):
            self._task_frames = {}
        if task.get("id"):
            self._task_frames[task.get("id")] = task_frame
        
        # Make the entire task clickable for editing (optimized event binding)
        task_frame.bind("<Button-1>", self._on_task_click)
        
        # Task checkbox
        is_completed = task.get("status") == "completed"
        checkbox = ctk.CTkCheckBox(task_frame, text="", width=18, height=18,
                                  command=lambda t=task: self.toggle_task_completion(t))
        checkbox.grid(row=0, column=0, padx=8, pady=8, sticky="nw")  # Reduced padding
        if is_completed:
            checkbox.select()
        
        # Task content area - now spans full width with buttons at bottom
        content_frame = ctk.CTkFrame(task_frame, fg_color=self.get_cached_color("surface_transparent"))
        content_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)  # Reduced padding
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=0)  # Title row - auto size based on content
        content_frame.grid_rowconfigure(1, weight=0)  # Description row - auto size based on content  
        content_frame.grid_rowconfigure(2, weight=0)  # Details row - auto size based on content
        content_frame.grid_rowconfigure(3, weight=1)  # Button row at bottom - takes remaining space
        content_frame.task_data = task
        content_frame.bind("<Button-1>", self._on_task_click)
        
        # Very conservative wrap length - the actual text area is much smaller than expected
        # Start with a low value that will definitely fit, then let it expand naturally
        try:
            frame_width = self.task_list_frame.winfo_width()
            if frame_width <= 200:  
                base_wrap_length = 200  # Very conservative
            else:
                # Much more conservative - only use 40% of frame width for text
                # This accounts for all the UI elements, padding, and margins
                base_wrap_length = max(200, int(frame_width * 0.4))
        except:
            base_wrap_length = 200  # Very conservative fallback
        
        # Task title with dynamic text wrapping and strikethrough for completed tasks
        task_text = task.get("title", "Untitled Task")
        if is_completed:
            task_text = f"~~{task_text}~~"  # Add strikethrough effect
            text_color = self.get_cached_color("text_muted")
            font_weight = "normal"
        else:
            text_color = self.get_cached_color("text_primary")
            font_weight = "bold"
            
        # Use cached fonts for major performance improvement
        task_font = self.get_cached_font('task_title_bold' if font_weight == "bold" else 'task_title_normal')
        task_label = ctk.CTkLabel(content_frame, text=task_text, 
                                 font=task_font,
                                 text_color=text_color,
                                 wraplength=base_wrap_length,  # Dynamic wrapping
                                 justify="left", anchor="w")
        task_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))  # Allow horizontal expansion and text wrapping
        task_label.task_data = task
        task_label.bind("<Button-1>", self._on_task_click)
        
        # Task description with dynamic wrapping (if present)
        description = task.get("description", "")
        if description:
            # Convert basic markdown to display text and show full description
            desc_text = self.convert_basic_markdown(description)
            
            # Allow much longer descriptions to wrap naturally - only truncate extremely long text
            max_display_length = 2000  # Very high limit - let wrapping handle most cases
            if len(desc_text) > max_display_length:
                desc_text = desc_text[:max_display_length] + "... (click to view full)"
            
            desc_label = ctk.CTkLabel(content_frame, text=desc_text, 
                                    font=self.get_cached_font('task_description'),
                                    text_color=self.get_cached_color("text_secondary"),
                                    wraplength=base_wrap_length,  # Dynamic wrapping
                                    justify="left", anchor="w")
            desc_label.grid(row=1, column=0, sticky="ew", pady=(0, 2))
            desc_label.task_data = task
            desc_label.bind("<Button-1>", self._on_task_click)
        
        # Task details (priority, time, etc.)
        details_text = []
        if task.get("priority") and task.get("priority") != "normal":
            details_text.append(f"Priority: {task.get('priority').title()}")
        if task.get("estimated_minutes"):
            details_text.append(f"{task.get('estimated_minutes')} min")
        
        if details_text:
            details_row = 2
            details_label = ctk.CTkLabel(content_frame, text=" • ".join(details_text), 
                                       font=self.get_cached_font('task_details'),
                                       text_color=self.get_cached_color("text_tertiary"),
                                       anchor="w")
            details_label.grid(row=details_row, column=0, sticky="ew", pady=(0, 2))
            details_label.task_data = task
            details_label.bind("<Button-1>", self._on_task_click)
        
        # Simplified action buttons (only show for non-completed tasks)
        if not is_completed:
            actions_frame = ctk.CTkFrame(content_frame, fg_color=self.get_cached_color("surface_transparent"))
            actions_frame.grid(row=3, column=0, sticky="se", pady=(2, 0))
            
            # Pre-compute button styles for performance
            if not hasattr(self, '_button_styles_cache'):
                self._button_styles_cache = {
                    'primary': get_button_colors("primary"),
                    'secondary': get_button_colors("secondary"),
                    'danger': get_button_colors("danger")
                }
            
            # Use cached fonts for buttons - major performance improvement 
            # Keep lambdas for buttons since CTkButton requires command parameter
            ai_btn = ctk.CTkButton(actions_frame, text="🤖", 
                                 width=28, height=26,
                                 command=lambda t=task: self.show_ai_assistant_dialog(t),
                                 **self._button_styles_cache['primary'],
                                 font=self.get_cached_font('button_medium'))
            ai_btn.grid(row=0, column=0, padx=1)
            
            # Add informative tooltip to AI button
            self.add_ai_tooltip(ai_btn, task)
            
            # Edit button
            edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=28, height=26,
                                   command=lambda t=task: self.edit_task(t),
                                   **self._button_styles_cache['secondary'],
                                   font=self.get_cached_font('button_small'))
            edit_btn.grid(row=0, column=1, padx=1)
            
            # Delete button
            delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=28, height=26,
                                     command=lambda t=task: self.delete_task(t),
                                     **self._button_styles_cache['danger'],
                                     font=self.get_cached_font('button_small'))
            delete_btn.grid(row=0, column=2, padx=1)
        
        # Return the task frame for potential incremental updates
        return task_frame
    
    def convert_basic_markdown(self, text):
        """Convert basic markdown to display-friendly text"""
        if not text:
            return text
            
        # Convert numbered lists (1. 2. 3.)
        import re
        text = re.sub(r'^(\d+)\.\s+', r'\1) ', text, flags=re.MULTILINE)
        
        # Convert bullet points (* - +)
        text = re.sub(r'^[*+-]\s+', r'• ', text, flags=re.MULTILINE)
        
        # Convert **bold** to visual emphasis (using Unicode)
        text = re.sub(r'\*\*(.*?)\*\*', r'𝗕\1𝗕', text)
        
        # Convert *italic* to visual emphasis 
        text = re.sub(r'\*(.*?)\*', r'𝘐\1𝘐', text)
        
        # Convert ## Headers to visual emphasis
        text = re.sub(r'^##\s+(.+)$', r'◆ \1 ◆', text, flags=re.MULTILINE)
        
        # Convert single # Headers 
        text = re.sub(r'^#\s+(.+)$', r'▶ \1 ◀', text, flags=re.MULTILINE)
        
        return text
    
    def format_for_detail_view(self, text):
        """Format text with simple, clean structure for better readability"""
        if not text:
            return text
            
        import re
        
        # Check if text is already formatted
        if '💡' in text and '• ' in text:
            return text  # Already formatted
        
        # Split into paragraphs and process each
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Handle numbered sections (1. 2. 3.) - keep them simple
            if re.match(r'^\d+\.\s+', paragraph):
                match = re.match(r'^(\d+)\.\s+(.+)', paragraph, re.DOTALL)
                if match:
                    number, content = match.groups()
                    # Simple section format
                    formatted_paragraphs.append(f"{number}. {content.split(':')[0]}:")
                    
                    # Handle sub-items on same line, separated by commas
                    if ':' in content:
                        rest = content.split(':', 1)[1].strip()
                        if rest:
                            sub_items = self._format_sub_items(rest)
                            formatted_paragraphs.extend(sub_items)
                    continue
            
            # Handle parenthetical content as tips
            if paragraph.strip().startswith('(') and paragraph.strip().endswith(')'):
                tip_text = paragraph.strip()[1:-1]
                formatted_paragraphs.append(f"💡 {tip_text}")
                continue
            
            # Handle comma-separated items
            if ',' in paragraph and any(word in paragraph.lower() for word in ['seconds', 'minutes', 'rounds']):
                sub_items = self._format_sub_items(paragraph)
                formatted_paragraphs.extend(sub_items)
            else:
                formatted_paragraphs.append(paragraph)
        
        # Join with single line breaks (not double)
        return '\n'.join(formatted_paragraphs)
    
    def _format_sub_items(self, text):
        """Format text into clean bullet points for sub-items"""
        import re
        
        items = []
        
        # Handle time-based items (30 seconds of X)
        time_pattern = r'(\d+\s+(?:seconds?|minutes?))\s+of\s+([^,\.]+)'
        time_matches = re.findall(time_pattern, text, re.IGNORECASE)
        if time_matches:
            for duration, activity in time_matches:
                items.append(f"• {duration} of {activity.strip()}")
            # Remove matched parts and continue with remaining text
            text = re.sub(time_pattern, '', text, flags=re.IGNORECASE)
        
        # Handle rounds/sets (3 rounds of X)
        rounds_pattern = r'(\d+\s+(?:rounds?|sets?))\s+of\s+([^,\.]+)'
        rounds_matches = re.findall(rounds_pattern, text, re.IGNORECASE)
        if rounds_matches:
            for sets, activity in rounds_matches:
                items.append(f"• {sets} of {activity.strip()}")
            text = re.sub(rounds_pattern, '', text, flags=re.IGNORECASE)
        
        # Handle simple comma-separated items
        if ',' in text:
            parts = text.split(',')
            for part in parts:
                part = part.strip().rstrip('.').strip()
                if part and len(part) > 2:
                    items.append(f"• {part}")
        
        # If no commas, just format as single item
        elif text.strip():
            items.append(f"• {text.strip()}")
        
        return items
    
    def _on_task_click(self, event):
        """Optimized task click handler - walks up widget tree to find task_data"""
        # Walk up the widget hierarchy to find task_data
        current_widget = event.widget
        while current_widget:
            if hasattr(current_widget, 'task_data'):
                self.edit_task(current_widget.task_data)
                return
            # Move up to parent widget
            current_widget = current_widget.master if hasattr(current_widget, 'master') else None
    
    def _on_ai_button_click(self, event):
        """Optimized AI button click handler"""
        widget = event.widget
        if hasattr(widget, 'task_data'):
            self.show_ai_assistant_dialog(widget.task_data)
    
    def _on_delete_button_click(self, event):
        """Optimized delete button click handler"""
        widget = event.widget
        if hasattr(widget, 'task_data'):
            self.delete_task(widget.task_data)
    
    def toggle_task_completion(self, task):
        """Toggle task completion status"""
        current_status = task.get("status", "pending")
        new_status = "completed" if current_status != "completed" else "pending"
        
        try:
            # Update task status via API
            task_id = task.get("id")
            is_completed = new_status == "completed"
            task_data = {
                "status": new_status,
                "is_completed": is_completed
            }
            response = requests.put(f"{self.api_base_url}/tasks/{task_id}", 
                                    json=task_data, timeout=5)
            
            if response.status_code == 200:
                # Update local task data
                task["status"] = new_status
                task["is_completed"] = is_completed
                
                # If this task is currently being edited, update the form
                if self.editing_task and self.selected_task and self.selected_task.get("id") == task_id:
                    self.status_var.set(new_status)
                
                # Refresh the task list to show updated status
                self.load_tasks_list(self.selected_project_id)
                
                # Refresh the project pane to show updated statistics (completion %, task counts, etc.)
                self.load_projects_list()
                
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
                    
                    # Refresh the project pane to show updated statistics (task count, completion %, etc.)
                    self.load_projects_list()
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
                                        font=self.get_cached_font('status'))
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=5)

    def load_projects_list(self):
        """Reload projects list (called when data changes)"""
        self.status_label.configure(text="Refreshing projects...")
        self.load_projects_data()
    
    def create_project_card(self, project):
        """Create a clickable project card in the sidebar with enhanced task statistics"""
        # Reduced card height for tighter layout
        card_frame = ctk.CTkFrame(self.projects_frame, height=85)  # Reduced from 95
        card_frame.grid(row=len(self.projects_frame.winfo_children()), column=0, sticky="ew", padx=3, pady=2)  # Reduced padding
        card_frame.grid_columnconfigure(1, weight=1)
        card_frame.grid_columnconfigure(2, weight=0)  # Actions column
        
        # Make the entire card clickable
        card_frame.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project icon/status indicator
        total_tasks = project.get("task_count", 0)
        completed_tasks = project.get("completed_tasks", 0)
        completion_percentage = project.get("completion_percentage", 0.0)
        
        # Choose icon based on completion status
        if total_tasks == 0:
            icon_text = "📝"  # Empty project
            icon_color = get_color("text_tertiary")
        elif completion_percentage == 100:
            icon_text = "✅"  # Completed project
            icon_color = get_color("success")
        elif completion_percentage > 0:
            icon_text = "🔄"  # In progress
            icon_color = get_color("primary")
        else:
            icon_text = "📋"  # Not started
            icon_color = get_color("text_secondary")
            
        icon_label = ctk.CTkLabel(card_frame, text=icon_text, font=self.get_cached_font('toolbar_large'))
        icon_label.grid(row=0, column=0, padx=10, pady=12, sticky="n")
        icon_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project name and details container
        details_frame = ctk.CTkFrame(card_frame, fg_color=get_color("surface_transparent"))
        details_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=8)
        details_frame.grid_columnconfigure(0, weight=1)  # Allow details to expand
        details_frame.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project name
        name_label = ctk.CTkLabel(details_frame, text=project["title"], 
                                 font=self.get_cached_font('project_title'),
                                 anchor="w")
        name_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        name_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Task statistics text
        if total_tasks > 0:
            pending_tasks = project.get("pending_tasks", 0)
            in_progress_tasks = project.get("in_progress_tasks", 0)
            
            stats_text = f"{completed_tasks}/{total_tasks} tasks completed"
            if in_progress_tasks > 0:
                stats_text += f" • {in_progress_tasks} in progress"
        else:
            stats_text = "No tasks yet"
            
        stats_label = ctk.CTkLabel(details_frame, text=stats_text,
                                  font=self.get_cached_font('project_stats'), 
                                  text_color=get_color("text_secondary"),
                                  anchor="w")
        stats_label.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        stats_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Progress bar (only show if there are tasks)
        if total_tasks > 0:
            progress_frame = ctk.CTkFrame(details_frame, fg_color=get_color("surface_transparent"), height=8)
            progress_frame.grid(row=2, column=0, sticky="ew", pady=(0, 2))
            progress_frame.grid_columnconfigure(0, weight=1)
            progress_frame.bind("<Button-1>", lambda e, p=project: self.select_project(p))
            
            # Background bar
            bg_bar = ctk.CTkFrame(progress_frame, height=6, 
                                 fg_color=get_color("progress_bg"))
            bg_bar.grid(row=0, column=0, sticky="ew", padx=1)
            bg_bar.bind("<Button-1>", lambda e, p=project: self.select_project(p))
            
            # Progress bar
            if completion_percentage > 0:
                progress_width = max(2, int(completion_percentage))  # Minimum 2% width for visibility
                
                # Choose color based on completion
                if completion_percentage == 100:
                    progress_color = get_color("success")
                elif completion_percentage >= 75:
                    progress_color = get_color("success_light")
                elif completion_percentage >= 50:
                    progress_color = get_color("primary")
                elif completion_percentage >= 25:
                    progress_color = get_color("warning")
                else:
                    progress_color = get_color("danger_light")
                
                progress_bar = ctk.CTkFrame(bg_bar, height=6, width=progress_width,
                                          fg_color=progress_color)
                progress_bar.place(relx=0, rely=0, relheight=1, relwidth=completion_percentage/100)
                progress_bar.bind("<Button-1>", lambda e, p=project: self.select_project(p))
            
            # Percentage text
            percentage_label = ctk.CTkLabel(details_frame, 
                                          text=f"{completion_percentage:.0f}%",
                                          font=self.get_cached_font('project_percentage'), 
                                          text_color=get_color("text_tertiary"),
                                          anchor="w")
            percentage_label.grid(row=3, column=0, sticky="ew")
            percentage_label.bind("<Button-1>", lambda e, p=project: self.select_project(p))
        
        # Project delete button
        delete_btn = ctk.CTkButton(card_frame, text="🗑️", width=30, height=30,
                                 command=lambda p=project: self.delete_project(p),
                                 fg_color=get_color("danger"),
                                 hover_color=get_color("danger_hover"),
                                 font=self.get_cached_font('label_small'))
        delete_btn.grid(row=0, column=2, padx=5, pady=12, sticky="n")
        
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
    
    def show_ai_assistant_dialog(self, task):
        """Show the AI assistant dialog with multiple capabilities"""
        try:
            # Immediate feedback in status bar
            self.status_label.configure(text="🤖 AI Assistant ready - select a capability to begin...")
            
            from .ai_split_dialog import show_ai_assistant_dialog
            
            def on_approve(preview_data):
                """Handle when user approves the AI changes"""
                self.execute_ai_changes(preview_data)
            
            def on_cancel():
                """Handle when user cancels the AI operation"""
                self.status_label.configure(text="AI operation cancelled")
                self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
            
            # Show the enhanced AI dialog
            show_ai_assistant_dialog(self.root, task, on_approve, on_cancel)
            
        except Exception as e:
            print(f"Error showing AI assistant dialog: {e}")
            self.status_label.configure(text="Error: Could not open AI assistant")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def show_ai_split_dialog(self, task):
        """Show the AI split task dialog (backward compatibility)"""
        try:
            # Immediate feedback in status bar
            self.status_label.configure(text="🤖 Starting AI task splitting - this may take 10-30 seconds...")
            
            from .ai_split_dialog import show_ai_split_dialog
            
            def on_approve(preview_data):
                """Handle when user approves the AI split"""
                self.execute_ai_changes(preview_data)
            
            def on_cancel():
                """Handle when user cancels the AI split"""
                self.status_label.configure(text="AI task splitting cancelled")
                self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
            
            # Show the AI dialog (backward compatibility)
            show_ai_split_dialog(self.root, task, on_approve, on_cancel)
            
        except Exception as e:
            print(f"Error showing AI split dialog: {e}")
            self.status_label.configure(text="Error: Could not open AI assistant")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def execute_ai_changes(self, preview_data):
        """Execute the AI changes after user approval (split or description improvement)"""
        try:
            preview_id = preview_data.get("preview_id")
            if not preview_id:
                self.status_label.configure(text="Error: Invalid preview data")
                return
            
            # Determine operation type from preview data
            proposed_changes = preview_data.get("proposed_changes", [])
            operation_type = "unknown"
            
            if any(change.get("action") == "create_tasks" for change in proposed_changes):
                operation_type = "split"
            elif any(change.get("action") == "update_task" for change in proposed_changes):
                operation_type = "description"
            
            # Show executing status based on operation
            if operation_type == "split":
                self.status_label.configure(text="🤖 Executing AI task split...")
            elif operation_type == "description":
                self.status_label.configure(text="🤖 Updating task description...")
            else:
                self.status_label.configure(text="🤖 Executing AI changes...")
            
            # Execute in background thread to avoid blocking UI
            def execute_changes():
                try:
                    response = requests.post(f"{self.api_base_url}/ai-agent/execute/{preview_id}", 
                                           timeout=600)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            # Success! Update UI on main thread safely
                            self.safe_ui_update(lambda: self.on_ai_success(result, operation_type))
                        else:
                            error_msg = result.get("error_message", "Unknown error")
                            self.safe_ui_update(lambda: self.on_ai_error(f"Operation failed: {error_msg}", operation_type))
                    else:
                        self.safe_ui_update(lambda: self.on_ai_error(f"API Error: {response.status_code}", operation_type))
                        
                except requests.exceptions.Timeout:
                    self.safe_ui_update(lambda: self.on_ai_error("Operation timed out", operation_type))
                except requests.exceptions.ConnectionError:
                    self.safe_ui_update(lambda: self.on_ai_error("Cannot connect to AI service", operation_type))
                except Exception as e:
                    self.safe_ui_update(lambda: self.on_ai_error(f"Unexpected error: {str(e)}", operation_type))
            
            # Start execution in background
            thread = threading.Thread(target=execute_changes, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error executing AI changes: {e}")
            self.status_label.configure(text="Error executing AI operation")
            self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def on_ai_success(self, result, operation_type):
        """Handle successful AI operation execution"""
        # Debug: Print the result to understand what we received
        print(f"DEBUG: AI success result: {result}")
        executed_changes = result.get("executed_changes", [])
        print(f"DEBUG: Executed changes: {executed_changes}")
        
        # Add a small delay to ensure backend has fully processed changes
        # then refresh the task list to show changes
        def delayed_refresh():
            if self.selected_project_id:
                print(f"DEBUG: Refreshing task list for project {self.selected_project_id}")
                # Force a complete reload from the server
                self.load_tasks_list(self.selected_project_id)
                
                # Also invalidate any cached task data to ensure fresh fetch
                if hasattr(self, 'tasks'):
                    print(f"DEBUG: Clearing cached tasks (had {len(self.tasks)} tasks)")
                    self.tasks = []
        
        # Delay refresh by 1000ms to ensure backend completion and database commit
        self.root.after(1000, delayed_refresh)
        
        # Show success message based on operation type
        executed_changes = result.get("executed_changes", [])
        
        if operation_type == "split":
            created_count = sum(1 for change in executed_changes if change.get("action") == "created_tasks")
            self.status_label.configure(text=f"✨ AI split complete! Created {created_count} subtasks")
            self.show_success_notification("Task Split Successfully!", 
                                         f"Your task has been intelligently divided into {created_count} manageable subtasks")
        elif operation_type == "description":
            updated_count = sum(1 for change in executed_changes if change.get("action") == "updated_task")
            self.status_label.configure(text=f"✨ Description improved! Updated {updated_count} task")
            self.show_success_notification("Description Improved Successfully!", 
                                         f"Your task description has been enhanced with more actionable details")
        else:
            self.status_label.configure(text="✨ AI operation completed successfully!")
            self.show_success_notification("AI Operation Complete!", 
                                         "Your task has been successfully processed by AI")
        
        self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
    
    def on_ai_error(self, error_message, operation_type):
        """Handle AI operation execution error"""
        if operation_type == "split":
            self.status_label.configure(text=f"❌ Split failed: {error_message}")
        elif operation_type == "description":
            self.status_label.configure(text=f"❌ Description update failed: {error_message}")
        else:
            self.status_label.configure(text=f"❌ AI operation failed: {error_message}")
        
        self.root.after(5000, lambda: self.status_label.configure(text="Ready"))
        print(f"AI operation error: {error_message}")
    
    # Keep backward compatibility method
    def on_split_success(self, result):
        """Handle successful AI split execution (backward compatibility)"""
        self.on_ai_success(result, "split")
    
    def on_split_error(self, error_message):
        """Handle AI split execution error (backward compatibility)"""
        self.on_ai_error(error_message, "split")
    
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
    
    def on_window_resize(self, event=None):
        """Handle window resize events to update text wrapping efficiently"""
        # Only refresh if the resize event is for the main window, not child widgets
        if event and event.widget == self.root:
            # Debounce the resize events - only refresh after 300ms of no resize
            if hasattr(self, '_resize_timer'):
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(300, self.update_text_wrapping)
    
    def update_text_wrapping(self):
        """Update text wrapping for existing task items without rebuilding the entire list"""
        try:
            # Get current frame width for wrap calculations
            if not hasattr(self, 'task_list_frame') or not self.task_list_frame.winfo_exists():
                return
                
            frame_width = self.task_list_frame.winfo_width()
            if frame_width <= 200:  # Skip if frame is too small or not initialized
                return
            
            # Calculate new wrap length - same very conservative logic as create_task_item
            base_wrap_length = max(200, int(frame_width * 0.4))
            
            # Update existing task labels instead of rebuilding everything
            for task_widget in self.task_list_frame.winfo_children():
                if hasattr(task_widget, 'winfo_children'):
                    self._update_task_widget_wrapping(task_widget, base_wrap_length)
                    
        except Exception as e:
            print(f"Error updating text wrapping: {e}")
            # Fallback to full refresh only if needed
            if hasattr(self, 'selected_project_id') and self.selected_project_id:
                self.load_tasks_list(self.selected_project_id)
    
    def _update_task_widget_wrapping(self, task_widget, wrap_length):
        """Update text wrapping for a single task widget"""
        try:
            # Find and update text labels within the task widget
            for child in task_widget.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ctk.CTkLabel):
                            # Update wraplength for labels that have text content
                            current_text = grandchild.cget("text")
                            if current_text and len(current_text) > 20:  # Only for longer text
                                grandchild.configure(wraplength=wrap_length)
        except Exception:
            pass  # Ignore errors in individual widget updates
    
    def run(self):
        """Start the main window"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run() 
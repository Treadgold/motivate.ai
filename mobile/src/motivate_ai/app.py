"""
Motivate.AI Mobile Application

Main application entry point for the BeeWare/Toga cross-platform app.
Provides task and project management with AI assistance.
"""

import asyncio
from datetime import datetime
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .services.api_client import APIClient, APIError
from .services.storage import StorageService
from .models.simple_models import Project, ProjectCreate, Task, TaskCreate
from .utils.helpers import format_datetime, format_duration
from . import DEFAULT_API_URL


class MotivateAIApp(toga.App):
    """Main Motivate.AI mobile application"""
    
    def __init__(self, *args, **kwargs):
        # Set required app metadata
        kwargs['formal_name'] = "Motivate.AI"
        kwargs['app_id'] = "ai.motivate.mobile"
        kwargs['description'] = "Task and project management with AI assistance"
        super().__init__(*args, **kwargs)
    
    def startup(self):
        """Initialize the application"""
        
        # Initialize services
        self.api_client = APIClient(DEFAULT_API_URL)
        self.storage = StorageService()
        
        # Application state
        self.projects = []
        self.tasks = []
        self.current_project = None
        self.current_task = None
        self.is_online = False
        
        # Navigation state
        self.current_view = "projects"  # projects, tasks, task_detail
        self.view_history = []
        
        # Create main UI
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.create_main_interface()
        
        # Load initial data
        self.add_background_task(self.initialize_data)
        
        self.main_window.show()

    def create_main_interface(self):
        """Create the main application interface with sliding panels"""
        # Create main container
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0))
        
        # Header with app title and navigation
        self.create_header(main_box)
        
        # Main content area with sliding panels - ensure proper width constraints
        self.content_container = toga.Box(style=Pack(
            direction=COLUMN,  # Changed to COLUMN for single-panel mobile view
            flex=1,
            padding=0,  # Remove any padding that might cause overflow
            width=549  # Explicit constraint to match available screen width
        ))
        main_box.add(self.content_container)
        
        # Create the three panels
        self.create_sliding_panels()
        
        # Status bar
        self.create_status_bar(main_box)
        
        # Set main window content
        self.main_window.content = main_box
        
        # Add keyboard shortcuts for navigation
        self.add_keyboard_shortcuts()
        
        # Show projects view by default
        self.show_view("projects")

    def create_header(self, parent_box):
        """Create application header with navigation"""
        header_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color="#f0f0f0"))
        
        # Back button (only show when not on projects view)
        self.back_button = toga.Button(
            "← Back",
            on_press=self.go_back,
            style=Pack(padding=2)
        )
        header_box.add(self.back_button)
        
        # Dynamic title based on current view
        self.title_label = toga.Label(
            "Projects",
            style=Pack(flex=1, text_align="center", font_size=16, font_weight="bold")
        )
        header_box.add(self.title_label)
        
        # Connection status indicator
        self.status_indicator = toga.Label(
            "🔴 Offline",
            style=Pack(text_align="right", font_size=12)
        )
        header_box.add(self.status_indicator)
        
        parent_box.add(header_box)

    def create_sliding_panels(self):
        """Create the three sliding panels"""
        # Projects panel (always visible, can be collapsed to left)
        self.projects_panel = toga.Box(style=Pack(
            direction=COLUMN, 
            flex=1,
            padding=5  # Reduced padding to prevent overflow
        ))
        
        # Tasks panel (slides in from right when project selected)
        self.tasks_panel = toga.Box(style=Pack(
            direction=COLUMN, 
            flex=1,
            padding=0,  # Zero padding for maximum space
            width=549  # Explicit width constraint
        ))
        
        # Task detail panel (slides in from right when task selected)
        self.task_detail_panel = toga.Box(style=Pack(
            direction=COLUMN, 
            flex=1,
            padding=5  # Reduced padding to prevent overflow
        ))
        
        # Add panels to container (only show current panel initially)
        self.content_container.add(self.projects_panel)
        
        # Create content for each panel
        self.create_projects_panel()
        self.create_tasks_panel()
        self.create_task_detail_panel()

    def create_status_bar(self, parent_box):
        """Create status bar"""
        status_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color="#f8f8f8"))
        
        self.status_label = toga.Label(
            "Ready",
            style=Pack(flex=1, text_align="left", font_size=10)
        )
        status_box.add(self.status_label)
        
        # Sync button
        self.sync_button = toga.Button(
            "🔄 Sync",
            on_press=self.sync_data,
            style=Pack(padding=2)
        )
        status_box.add(self.sync_button)
        
        # Settings button
        settings_button = toga.Button(
            "⚙️",
            on_press=self.show_settings_dialog,
            style=Pack(padding=2)
        )
        status_box.add(settings_button)
        
        parent_box.add(status_box)

    def add_keyboard_shortcuts(self):
        """Add keyboard shortcuts for navigation"""
        # Note: Toga keyboard handling might be limited on mobile, but this provides structure
        # These would work better on desktop versions
        try:
            # ESC or Back key to go back
            if hasattr(self.main_window, 'on_key_press'):
                self.main_window.on_key_press = self.handle_key_press
        except AttributeError:
            # Keyboard handling not available on this platform
            pass

    def handle_key_press(self, widget, key):
        """Handle keyboard navigation"""
        if key == 'Escape' or key == 'Back':
            if self.current_view != "projects":
                self.go_back(None)
        elif key == 'Left':
            if self.current_view == "tasks" and len(self.projects) > 1:
                self.switch_to_previous_project(None)
        elif key == 'Right':
            if self.current_view == "tasks" and len(self.projects) > 1:
                self.switch_to_next_project(None)

    def create_projects_panel(self):
        """Create projects panel content"""
        # Projects panel will be populated dynamically by refresh methods
        # This ensures clean switching between full and minimal views
        pass
        
    def create_tasks_panel(self):
        """Create tasks panel content"""
        # Tasks header
        header_box = toga.Box(style=Pack(
            direction=ROW, 
            padding=0,  # Zero padding
            width=549  # Explicit width constraint to prevent overflow
        ))
        
        # Project navigation (when multiple projects exist)
        self.prev_project_button = toga.Button(
            "◀",
            on_press=self.switch_to_previous_project,
            style=Pack(padding=0, font_size=8)  # Zero padding, smaller font
        )
        header_box.add(self.prev_project_button)
        
        self.tasks_title = toga.Label(
            "Tasks",
            style=Pack(flex=1, font_size=12, font_weight="bold", text_align="center")
        )
        header_box.add(self.tasks_title)
        
        self.next_project_button = toga.Button(
            "▶",
            on_press=self.switch_to_next_project,
            style=Pack(padding=0, font_size=8)  # Zero padding, smaller font
        )
        header_box.add(self.next_project_button)
        
        # Add task button
        add_task_button = toga.Button(
            "+",  # Shortened to just plus symbol
            on_press=self.show_new_task_dialog,
            style=Pack(padding=0, font_size=14)  # Zero padding, smaller font
        )
        header_box.add(add_task_button)
        
        self.tasks_panel.add(header_box)
        
        # Tasks list container - optimized for natural page scrolling
        self.tasks_list_container = toga.ScrollContainer(style=Pack(flex=1))
        self.tasks_panel.add(self.tasks_list_container)
        
    def create_task_detail_panel(self):
        """Create task detail panel content"""
        # Task detail header
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        self.task_detail_title = toga.Label(
            "Task Details",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        header_box.add(self.task_detail_title)
        
        # Save button
        save_button = toga.Button(
            "💾 Save",
            on_press=self.save_task_changes,
            style=Pack(padding=2)
        )
        header_box.add(save_button)
        
        self.task_detail_panel.add(header_box)
        
        # Task detail form container
        self.task_detail_container = toga.ScrollContainer(style=Pack(flex=1))
        self.task_detail_panel.add(self.task_detail_container)

    def show_view(self, view_name):
        """Navigate to a specific view with sliding animation"""
        if view_name == self.current_view:
            return
            
        # Add current view to history if moving forward
        if view_name != "projects" and self.current_view not in self.view_history:
            self.view_history.append(self.current_view)
        
        # Clear content container
        self.content_container.clear()
        
        # Update current view
        self.current_view = view_name
        
        # Show appropriate panel(s)
        if view_name == "projects":
            # Full screen projects view
            self.content_container.add(self.projects_panel)
            self.projects_panel.style.flex = 1
            self.title_label.text = "Projects"
            self.back_button.enabled = False
            self.refresh_projects_list()
            
        elif view_name == "tasks":
            # Show only tasks panel - full screen focus
            self.content_container.add(self.tasks_panel)
            self.tasks_panel.style.flex = 1  # Full screen
            
            project_name = self.current_project.title if self.current_project else "Tasks"
            self.title_label.text = f"{project_name} - Tasks"
            self.tasks_title.text = f"Tasks in {project_name}"
            self.back_button.enabled = True
            self.refresh_tasks_list()
            
        elif view_name == "task_detail":
            # Full screen task detail view
            self.content_container.add(self.task_detail_panel)
            self.task_detail_panel.style.flex = 1
            
            task_name = self.current_task.title if self.current_task else "Task"
            self.title_label.text = f"Edit: {task_name}"
            self.task_detail_title.text = f"Editing: {task_name}"
            self.back_button.enabled = True
            self.refresh_task_detail()
            
    def go_back(self, widget):
        """Navigate back to previous view"""
        if self.current_view == "task_detail":
            self.show_view("tasks")
        elif self.current_view == "tasks":
            self.show_view("projects")

    def refresh_projects_list(self):
        """Refresh the projects list"""
        # Clear the entire projects panel and rebuild it for full view
        self.projects_panel.clear()
        
        # Re-add the header for full projects view
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        projects_title = toga.Label(
            "My Projects",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        header_box.add(projects_title)
        
        # Add project button
        add_project_button = toga.Button(
            "➕ NEW",
            on_press=self.show_new_project_dialog,
            style=Pack(padding=2)
        )
        header_box.add(add_project_button)
        
        self.projects_panel.add(header_box)
        
        # Projects list content
        projects_box = toga.Box(style=Pack(direction=COLUMN))
        
        if not self.projects:
            no_projects_label = toga.Label(
                "No projects yet. Tap 'New Project' to get started!",
                style=Pack(padding=20, text_align="center")
            )
            projects_box.add(no_projects_label)
        else:
            for project in self.projects:
                project_card = self.create_project_card(project)
                projects_box.add(project_card)
        
        # Recreate the scroll container
        self.projects_list_container = toga.ScrollContainer(style=Pack(flex=1))
        self.projects_list_container.content = projects_box
        self.projects_panel.add(self.projects_list_container)
        

    def refresh_tasks_list(self):
        """Refresh the tasks list for current project with full-width optimization"""
        # Update project navigation button visibility
        if hasattr(self, 'prev_project_button') and hasattr(self, 'next_project_button'):
            if self.projects and len(self.projects) > 1:
                self.prev_project_button.enabled = True
                self.next_project_button.enabled = True
            else:
                self.prev_project_button.enabled = False
                self.next_project_button.enabled = False
        
        tasks_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=0,  # Zero padding for maximum space usage
            width=549  # Explicit width constraint to prevent overflow
        ))
        
        # Filter tasks for current project
        project_tasks = []
        if self.current_project:
            project_tasks = [t for t in self.tasks if t.project_id == self.current_project.id]
        
        if not project_tasks:
            no_tasks_label = toga.Label(
                "No tasks yet. Tap 'New Task' to get started!",
                style=Pack(padding=20, text_align="center", font_size=16)
            )
            tasks_box.add(no_tasks_label)
        else:
            for i, task in enumerate(project_tasks):
                task_card = self.create_task_card(task)
                tasks_box.add(task_card)
                
                # Add spacing between cards (except after the last one)
                if i < len(project_tasks) - 1:
                    spacer = toga.Box(style=Pack(padding=1))  # Minimal space between cards
                    tasks_box.add(spacer)
        
        self.tasks_list_container.content = tasks_box
        
    def refresh_task_detail(self):
        """Refresh the task detail form"""
        detail_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        if not self.current_task:
            error_label = toga.Label(
                "No task selected",
                style=Pack(padding=20, text_align="center")
            )
            detail_box.add(error_label)
        else:
            # Task title input
            title_label = toga.Label("Title:", style=Pack(padding=2, font_weight="bold"))
            detail_box.add(title_label)
            
            self.task_title_input = toga.TextInput(
                value=self.current_task.title,
                style=Pack(padding=5)
            )
            detail_box.add(self.task_title_input)
            
            # Task description input
            desc_label = toga.Label("Description:", style=Pack(padding=2, font_weight="bold"))
            detail_box.add(desc_label)
            
            self.task_desc_input = toga.MultilineTextInput(
                value=self.current_task.description or "",
                style=Pack(padding=5, flex=1)
            )
            detail_box.add(self.task_desc_input)
            
            # Priority selection
            priority_label = toga.Label("Priority:", style=Pack(padding=2, font_weight="bold"))
            detail_box.add(priority_label)
            
            self.task_priority_selection = toga.Selection(
                items=["low", "normal", "medium", "high"],
                value=self.current_task.priority,
                style=Pack(padding=3)  # Reduced padding
            )
            detail_box.add(self.task_priority_selection)
            
            # Status toggle
            self.task_completed_switch = toga.Switch(
                text="Completed",
                value=self.current_task.is_completed,
                style=Pack(padding=5)
            )
            detail_box.add(self.task_completed_switch)
        
        self.task_detail_container.content = detail_box

    def create_project_card(self, project: Project):
        """Create a clickable project card widget"""
        # Main card button (entire card is clickable)
        card_button = toga.Button(
            "",  # No text, we'll add content as a box
            on_press=lambda w, p=project: self.view_project_tasks(p),
            style=Pack(
                direction=COLUMN,
                padding=0,
                background_color="#f5f5f5"
            )
        )
        
        # Create card content box
        card_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10
        ))
        
        # Project header
        header_box = toga.Box(style=Pack(direction=ROW))
        
        # Project icon and title
        title_text = f"{project.status_icon} {project.title}"
        title_label = toga.Label(
            title_text,
            style=Pack(flex=1, font_weight="bold", font_size=14)
        )
        header_box.add(title_label)
        
        # Arrow indicator
        arrow_label = toga.Label(
            "→",
            style=Pack(font_size=16, color="#666")
        )
        header_box.add(arrow_label)
        
        card_box.add(header_box)
        
        # Project stats
        if project.task_count > 0:
            stats_label = toga.Label(
                project.status_text,
                style=Pack(font_size=12, color="#666")
            )
            card_box.add(stats_label)
            
            # Progress bar (simplified)
            progress_text = f"Progress: {project.completion_percentage:.0f}%"
            progress_label = toga.Label(
                progress_text,
                style=Pack(font_size=11, color="#888")
            )
            card_box.add(progress_label)
        
        # Description if available - natural text display that expands cards
        if project.description:
            # Use Label that naturally expands the card height for long text
            desc_label = toga.Label(
                project.description,
                style=Pack(
                    font_size=11, 
                    color="#555",
                    text_align="left",
                    padding=(4, 2),  # Comfortable padding for readability
                    flex=1  # Allow natural text flow and card expansion
                )
            )
            card_box.add(desc_label)
        
        # For Toga, we can't put content inside a button easily, so let's use a regular box with click handling
        # We'll make the entire card respond to clicks differently
        
        # Create a container that looks like a card
        card_container = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            background_color="#f5f5f5"
        ))
        
        # Add tap handler by making it a button-like experience
        # Since we can't make the box clickable directly, we'll add a button that spans the card
        tap_button = toga.Button(
            "Tap to view tasks →",
            on_press=lambda w, p=project: self.view_project_tasks(p),
            style=Pack(padding=5, background_color="#e0e0e0")
        )
        
        card_container.add(card_box)
        card_container.add(tap_button)
        
        return card_container

    def view_project_tasks(self, project: Project):
        """Navigate to tasks view for a specific project"""
        self.current_project = project
        self.show_view("tasks")

    def view_task_detail(self, task: Task):
        """Navigate to task detail view for a specific task"""
        self.current_task = task
        self.show_view("task_detail")

    def switch_to_previous_project(self, widget):
        """Switch to the previous project in the list"""
        if self.current_project and self.projects and len(self.projects) > 1:
            current_index = next((i for i, p in enumerate(self.projects) if p.id == self.current_project.id), 0)
            previous_index = (current_index - 1) % len(self.projects)
            self.current_project = self.projects[previous_index]
            self.refresh_tasks_list()
            # Update title to reflect new project
            self.title_label.text = f"{self.current_project.title} - Tasks"
            self.tasks_title.text = f"Tasks in {self.current_project.title}"

    def switch_to_next_project(self, widget):
        """Switch to the next project in the list"""
        if self.current_project and self.projects and len(self.projects) > 1:
            current_index = next((i for i, p in enumerate(self.projects) if p.id == self.current_project.id), 0)
            next_index = (current_index + 1) % len(self.projects)
            self.current_project = self.projects[next_index]
            self.refresh_tasks_list()
            # Update title to reflect new project
            self.title_label.text = f"{self.current_project.title} - Tasks"
            self.tasks_title.text = f"Tasks in {self.current_project.title}"

    def create_task_card(self, task: Task):
        """Create a clickable task card widget optimized for full-width display"""
        # Create a container that looks like a card with minimal padding to prevent overflow
        card_container = toga.Box(style=Pack(
            direction=COLUMN,
            padding=1,  # Ultra minimal padding
            background_color="#ffffff" if not task.is_completed else "#f0f8f0",
            width=540  # Explicit width constraint to fit within 549px screen
        ))
        
        # Task content box - allow natural height expansion
        card_box = toga.Box(style=Pack(
            direction=COLUMN
        ))
        
        # Task header
        header_box = toga.Box(style=Pack(direction=ROW))
        
        # Completion checkbox
        checkbox = toga.Switch(
            text="",
            value=task.is_completed,
            on_change=lambda w, t=task: self.toggle_task_completion(t),
            style=Pack(padding=0)  # Zero padding
        )
        header_box.add(checkbox)
        
        # Task title with status - improved word wrapping
        title_text = f"{task.status_icon} {task.title}"
        if task.is_completed:
            title_text = f"✅ {task.title}"
        
        title_label = toga.Label(
            title_text,
            style=Pack(
                flex=1, 
                font_weight="bold", 
                font_size=12,  # Further reduced
                text_align="left",
                padding_right=2,  # Minimal padding
                width=250  # Conservative width constraint to prevent overflow
            )
        )
        header_box.add(title_label)
        
        # Priority indicator
        priority_label = toga.Label(
            task.priority_icon,
            style=Pack(padding=0)  # Zero padding
        )
        header_box.add(priority_label)
        
        card_box.add(header_box)
        
        # Task details
        details_box = toga.Box(style=Pack(direction=ROW))
        
        # Time estimate
        time_label = toga.Label(
            f"⏱️ {task.display_time}",
            style=Pack(font_size=8, color="#666", padding=0)  # Even smaller font, no padding
        )
        details_box.add(time_label)
        
        card_box.add(details_box)
        
        # Description if available - using MultilineTextInput for proper wrapping
        if task.description:
            # Break long text into shorter lines for better display
            lines = []
            words = task.description.split()
            current_line = ""
            max_chars_per_line = 60  # Adjust based on screen width
            
            for word in words:
                if len(current_line + " " + word) > max_chars_per_line:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        current_line = word
                else:
                    current_line = current_line + " " + word if current_line else word
            
            if current_line:
                lines.append(current_line)
            
            # Create a label with the formatted text
            desc_label = toga.Label(
                "\n".join(lines),
                style=Pack(
                    font_size=9,
                    color="#555",
                    text_align="left",
                    padding=(1, 1),
                    width=530
                )
            )
            card_box.add(desc_label)
        
        # Add content to container
        card_container.add(card_box)
        
        # Add edit button with minimal padding to prevent overflow
        edit_button = toga.Button(
            "EDIT",  # Much shorter text
            on_press=lambda w, t=task: self.view_task_detail(t),
            style=Pack(
                padding=2,  # Further reduced
                background_color="#007acc", 
                color="#ffffff", 
                font_weight="bold",
                font_size=10,  # Smaller font
                width=530  # Explicit width constraint to match card content
            )
        )
        card_container.add(edit_button)
        
        return card_container

    def save_task_changes(self, widget):
        """Save changes to the current task"""
        if not self.current_task:
            return
            
        try:
            # Update task with form values
            self.current_task.title = self.task_title_input.value
            self.current_task.description = self.task_desc_input.value
            self.current_task.priority = self.task_priority_selection.value
            self.current_task.is_completed = self.task_completed_switch.value
            
            # Save to API or local storage
            if self.is_online:
                # TODO: Add API update call
                self.update_status("Task updated online")
            else:
                self.update_status("Task updated locally")
            
            # Save to local storage
            self.storage.save_tasks(self.tasks)
            
            # Refresh the current view
            self.refresh_task_detail()
            
        except Exception as e:
            self.update_status(f"Error saving task: {str(e)}")
            
    def show_settings_dialog(self, widget):
        """Show settings dialog"""
        # For now, just show API URL update
        self.add_background_task(self.show_api_settings_dialog)
        
    async def show_api_settings_dialog(self):
        """Show API settings dialog"""
        current_url = self.api_client.base_url
        new_url = await self.main_window.question_dialog(
            "API Settings",
            f"Current API URL: {current_url}\n\nEnter new API URL:"
        )
        
        if new_url and new_url != current_url:
            self.api_client = APIClient(new_url)
            self.update_status("API URL updated")
            # Re-check connection
            await self.check_connection()

    # Event handlers
    async def initialize_data(self, widget=None):
        """Initialize application data"""
        self.update_status("Loading data...")
        
        # Try to load from API first
        try:
            await self.check_connection()
            if self.is_online:
                await self.load_data_from_api()
            else:
                self.load_data_from_storage()
        except Exception as e:
            print(f"Error initializing data: {e}")
            self.load_data_from_storage()
        
        self.update_status("Ready")
        self.refresh_current_view()

    async def check_connection(self, widget=None):
        """Check API connection status"""
        try:
            self.is_online = await self.api_client.health_check()
            if self.is_online:
                self.status_indicator.text = "🟢 Online"
            else:
                self.status_indicator.text = "🔴 Offline"
        except Exception:
            self.is_online = False
            self.status_indicator.text = "🔴 Offline"

    async def load_data_from_api(self):
        """Load data from API"""
        try:
            self.projects = await self.api_client.get_projects()
            self.tasks = await self.api_client.get_tasks()
            
            # Save to local storage
            self.storage.save_projects(self.projects)
            self.storage.save_tasks(self.tasks)
            
        except APIError as e:
            print(f"API Error: {e}")
            self.load_data_from_storage()

    def load_data_from_storage(self):
        """Load data from local storage"""
        self.projects = self.storage.load_projects()
        self.tasks = self.storage.load_tasks()

    async def sync_data(self, widget=None):
        """Sync data with backend"""
        self.update_status("Syncing...")
        
        try:
            await self.check_connection()
            if self.is_online:
                await self.load_data_from_api()
                self.update_status("Sync completed")
                self.refresh_current_view()
            else:
                self.update_status("Cannot sync - offline")
        except Exception as e:
            self.update_status(f"Sync failed: {str(e)}")



    async def toggle_task_completion(self, task: Task):
        """Toggle task completion status"""
        try:
            if self.is_online:
                updated_task = await self.api_client.toggle_task_completion(task.id)
                # Update local task
                for i, t in enumerate(self.tasks):
                    if t.id == task.id:
                        self.tasks[i] = updated_task
                        break
                self.storage.save_tasks(self.tasks)
            else:
                # Update locally only
                toggled_task = task.toggle_completion()
                for i, t in enumerate(self.tasks):
                    if t.id == task.id:
                        self.tasks[i] = toggled_task
                        break
                self.storage.save_tasks(self.tasks)
            
            # Refresh current view
            if self.current_view == "tasks":
                self.refresh_tasks_list()
            elif self.current_view == "task_detail":
                self.refresh_task_detail()
            
        except Exception as e:
            self.update_status(f"Error updating task: {str(e)}")

    async def show_new_project_dialog(self, widget):
        """Show new project dialog"""
        # For now, create a simple project
        # In a full implementation, this would show a proper dialog
        project_name = await self.main_window.question_dialog(
            "New Project",
            "Enter project name:"
        )
        
        if project_name:
            await self.create_project(project_name)

    async def show_new_task_dialog(self, widget):
        """Show new task dialog"""
        # For now, create a simple task
        # In a full implementation, this would show a proper dialog
        task_name = await self.main_window.question_dialog(
            "New Task", 
            "Enter task name:"
        )
        
        if task_name:
            await self.create_task(task_name)

    async def create_project(self, name: str):
        """Create a new project"""
        try:
            project_data = ProjectCreate(title=name)
            
            if self.is_online:
                new_project = await self.api_client.create_project(project_data)
                self.projects.append(new_project)
                self.storage.save_projects(self.projects)
            else:
                # Create locally with temporary ID
                import time
                temp_id = int(time.time())
                new_project = Project(
                    id=temp_id,
                    title=name,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.projects.append(new_project)
                self.storage.save_projects(self.projects)
            
            self.update_status(f"Project '{name}' created")
            self.refresh_current_view()
            
        except Exception as e:
            self.update_status(f"Error creating project: {str(e)}")

    async def create_task(self, name: str):
        """Create a new task"""
        try:
            # Use current project if available
            project_id = self.current_project.id if self.current_project else None
            if not project_id and self.projects:
                project_id = self.projects[0].id
            
            task_data = TaskCreate(title=name, project_id=project_id)
            
            if self.is_online:
                new_task = await self.api_client.create_task(task_data)
                self.tasks.append(new_task)
                self.storage.save_tasks(self.tasks)
            else:
                # Create locally with temporary ID
                import time
                temp_id = int(time.time())
                new_task = Task(
                    id=temp_id,
                    title=name,
                    project_id=project_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.tasks.append(new_task)
                self.storage.save_tasks(self.tasks)
            
            self.update_status(f"Task '{name}' created")
            self.refresh_current_view()
            
        except Exception as e:
            self.update_status(f"Error creating task: {str(e)}")



    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.text = message

    def refresh_current_view(self):
        """Refresh the current view"""
        if self.current_view == "projects":
            self.refresh_projects_list()
        elif self.current_view == "tasks":
            self.refresh_tasks_list()
        elif self.current_view == "task_detail":
            self.refresh_task_detail()


def main():
    """Main entry point"""
    return MotivateAIApp()


if __name__ == '__main__':
    app = main()
    app.main_loop()
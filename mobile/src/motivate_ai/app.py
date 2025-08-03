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
        self.is_online = False
        
        # Create main UI
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.create_main_interface()
        
        # Load initial data
        self.add_background_task(self.initialize_data)
        
        self.main_window.show()

    def create_main_interface(self):
        """Create the main application interface"""
        # Create main container
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Header with app title and status
        self.create_header(main_box)
        
        # Navigation tabs
        self.create_navigation(main_box)
        
        # Content area (will be populated based on current tab)
        self.content_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        main_box.add(self.content_box)
        
        # Status bar
        self.create_status_bar(main_box)
        
        # Set main window content
        self.main_window.content = main_box
        
        # Show projects by default
        self.show_projects_view()

    def create_header(self, parent_box):
        """Create application header"""
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # App title
        title_label = toga.Label(
            "Motivate.AI",
            style=Pack(flex=1, text_align="left", font_size=18, font_weight="bold")
        )
        header_box.add(title_label)
        
        # Connection status indicator
        self.status_indicator = toga.Label(
            "🔴 Offline",
            style=Pack(text_align="right", font_size=12)
        )
        header_box.add(self.status_indicator)
        
        parent_box.add(header_box)

    def create_navigation(self, parent_box):
        """Create navigation tabs"""
        nav_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # Projects tab
        self.projects_button = toga.Button(
            "📁 Projects",
            on_press=self.show_projects_view,
            style=Pack(flex=1, padding=5)
        )
        nav_box.add(self.projects_button)
        
        # Tasks tab
        self.tasks_button = toga.Button(
            "📝 Tasks", 
            on_press=self.show_tasks_view,
            style=Pack(flex=1, padding=5)
        )
        nav_box.add(self.tasks_button)
        
        # Settings tab
        self.settings_button = toga.Button(
            "⚙️ Settings",
            on_press=self.show_settings_view,
            style=Pack(flex=1, padding=5)
        )
        nav_box.add(self.settings_button)
        
        parent_box.add(nav_box)

    def create_status_bar(self, parent_box):
        """Create status bar"""
        status_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
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
        
        parent_box.add(status_box)

    def show_projects_view(self, widget=None):
        """Show projects view"""
        self.content_box.clear()
        
        # Projects header
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        projects_title = toga.Label(
            "Projects",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        header_box.add(projects_title)
        
        # Add project button
        add_project_button = toga.Button(
            "➕ New Project",
            on_press=self.show_new_project_dialog,
            style=Pack(padding=2)
        )
        header_box.add(add_project_button)
        
        self.content_box.add(header_box)
        
        # Projects list
        self.create_projects_list()

    def create_projects_list(self):
        """Create projects list view"""
        if not self.projects:
            no_projects_label = toga.Label(
                "No projects yet. Tap 'New Project' to get started!",
                style=Pack(padding=20, text_align="center")
            )
            self.content_box.add(no_projects_label)
            return
        
        # Create scrollable container for projects
        projects_scroll = toga.ScrollContainer(style=Pack(flex=1))
        projects_box = toga.Box(style=Pack(direction=COLUMN))
        
        for project in self.projects:
            project_card = self.create_project_card(project)
            projects_box.add(project_card)
        
        projects_scroll.content = projects_box
        self.content_box.add(projects_scroll)

    def create_project_card(self, project: Project):
        """Create a project card widget"""
        card_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            background_color="#f5f5f5"
        ))
        
        # Project header
        header_box = toga.Box(style=Pack(direction=ROW))
        
        # Project icon and title
        title_text = f"{project.status_icon} {project.title}"
        title_label = toga.Label(
            title_text,
            style=Pack(flex=1, font_weight="bold")
        )
        header_box.add(title_label)
        
        # Project actions
        view_button = toga.Button(
            "View",
            on_press=lambda w, p=project: self.view_project_tasks(p),
            style=Pack(padding=2)
        )
        header_box.add(view_button)
        
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
        
        # Description if available
        if project.description:
            desc_label = toga.Label(
                project.description[:100] + ("..." if len(project.description) > 100 else ""),
                style=Pack(font_size=11, color="#555")
            )
            card_box.add(desc_label)
        
        return card_box

    def show_tasks_view(self, widget=None):
        """Show tasks view"""
        self.content_box.clear()
        
        # Tasks header
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        tasks_title = toga.Label(
            "Tasks",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        header_box.add(tasks_title)
        
        # Add task button
        add_task_button = toga.Button(
            "➕ New Task",
            on_press=self.show_new_task_dialog,
            style=Pack(padding=2)
        )
        header_box.add(add_task_button)
        
        self.content_box.add(header_box)
        
        # Project filter if multiple projects
        if len(self.projects) > 1:
            self.create_project_filter()
        
        # Tasks list
        self.create_tasks_list()

    def create_project_filter(self):
        """Create project filter dropdown"""
        filter_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        filter_label = toga.Label("Filter by project:", style=Pack(padding=5))
        filter_box.add(filter_label)
        
        # Create project selection
        project_choices = ["All Projects"] + [p.title for p in self.projects]
        self.project_filter = toga.Selection(
            items=project_choices,
            on_select=self.filter_tasks_by_project,
            style=Pack(flex=1, padding=5)
        )
        filter_box.add(self.project_filter)
        
        self.content_box.add(filter_box)

    def create_tasks_list(self):
        """Create tasks list view"""
        filtered_tasks = self.get_filtered_tasks()
        
        if not filtered_tasks:
            no_tasks_label = toga.Label(
                "No tasks yet. Tap 'New Task' to get started!",
                style=Pack(padding=20, text_align="center")
            )
            self.content_box.add(no_tasks_label)
            return
        
        # Create scrollable container for tasks
        tasks_scroll = toga.ScrollContainer(style=Pack(flex=1))
        tasks_box = toga.Box(style=Pack(direction=COLUMN))
        
        for task in filtered_tasks:
            task_card = self.create_task_card(task)
            tasks_box.add(task_card)
        
        tasks_scroll.content = tasks_box
        self.content_box.add(tasks_scroll)

    def create_task_card(self, task: Task):
        """Create a task card widget"""
        card_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            background_color="#f9f9f9"
        ))
        
        # Task header
        header_box = toga.Box(style=Pack(direction=ROW))
        
        # Completion checkbox
        checkbox = toga.Switch(
            text="",
            value=task.is_completed,
            on_toggle=lambda w, t=task: self.toggle_task_completion(t),
            style=Pack(padding=2)
        )
        header_box.add(checkbox)
        
        # Task title with status
        title_text = f"{task.status_icon} {task.title}"
        if task.is_completed:
            title_text = f"✅ {task.title}"
        
        title_label = toga.Label(
            title_text,
            style=Pack(flex=1, font_weight="bold")
        )
        header_box.add(title_label)
        
        # Priority indicator
        priority_label = toga.Label(
            task.priority_icon,
            style=Pack(padding=2)
        )
        header_box.add(priority_label)
        
        card_box.add(header_box)
        
        # Task details
        details_box = toga.Box(style=Pack(direction=ROW))
        
        # Time estimate
        time_label = toga.Label(
            f"⏱️ {task.display_time}",
            style=Pack(font_size=11, color="#666", padding=2)
        )
        details_box.add(time_label)
        
        # Project name if available
        if task.project_id and self.projects:
            project = next((p for p in self.projects if p.id == task.project_id), None)
            if project:
                project_label = toga.Label(
                    f"📁 {project.title}",
                    style=Pack(font_size=11, color="#666", padding=2)
                )
                details_box.add(project_label)
        
        card_box.add(details_box)
        
        # Description if available
        if task.description:
            desc_label = toga.Label(
                task.description[:100] + ("..." if len(task.description) > 100 else ""),
                style=Pack(font_size=11, color="#555")
            )
            card_box.add(desc_label)
        
        return card_box

    def show_settings_view(self, widget=None):
        """Show settings view"""
        self.content_box.clear()
        
        settings_title = toga.Label(
            "Settings",
            style=Pack(font_size=16, font_weight="bold", padding=5)
        )
        self.content_box.add(settings_title)
        
        # Connection settings
        connection_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        api_label = toga.Label("API Server URL:", style=Pack(padding=2))
        connection_box.add(api_label)
        
        self.api_url_input = toga.TextInput(
            value=self.api_client.base_url,
            style=Pack(padding=2)
        )
        connection_box.add(self.api_url_input)
        
        update_api_button = toga.Button(
            "Update API URL",
            on_press=self.update_api_url,
            style=Pack(padding=5)
        )
        connection_box.add(update_api_button)
        
        self.content_box.add(connection_box)
        
        # Storage info
        storage_info = self.storage.get_storage_info()
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        info_title = toga.Label("Storage Information:", style=Pack(font_weight="bold"))
        info_box.add(info_title)
        
        for key, value in storage_info.items():
            info_text = f"{key.replace('_', ' ').title()}: {value}"
            info_label = toga.Label(info_text, style=Pack(font_size=11, padding=1))
            info_box.add(info_label)
        
        self.content_box.add(info_box)

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

    def get_filtered_tasks(self):
        """Get tasks filtered by current selection"""
        if hasattr(self, 'project_filter') and self.project_filter.value != "All Projects":
            project_name = self.project_filter.value
            project = next((p for p in self.projects if p.title == project_name), None)
            if project:
                return [t for t in self.tasks if t.project_id == project.id]
        
        return self.tasks

    def filter_tasks_by_project(self, widget):
        """Handle project filter change"""
        self.create_tasks_list()

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
            
            self.refresh_current_view()
            
        except Exception as e:
            self.update_status(f"Error updating task: {str(e)}")

    def view_project_tasks(self, project: Project):
        """View tasks for a specific project"""
        self.current_project = project
        self.show_tasks_view()
        
        # Set project filter if it exists
        if hasattr(self, 'project_filter'):
            self.project_filter.value = project.title

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

    def update_api_url(self, widget):
        """Update API URL"""
        new_url = self.api_url_input.value.strip()
        if new_url:
            self.api_client = APIClient(new_url)
            self.update_status("API URL updated")
            # Re-check connection
            self.add_background_task(self.check_connection)

    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.text = message

    def refresh_current_view(self):
        """Refresh the current view"""
        # This is a simplified refresh - in a full implementation,
        # you'd want to detect which view is currently active
        pass


def main():
    """Main entry point"""
    return MotivateAIApp()


if __name__ == '__main__':
    app = main()
    app.main_loop()
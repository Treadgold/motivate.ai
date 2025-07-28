"""
Smart Pop-up Interruption System for Motivate.AI

Manages intelligent pop-up notifications that appear at optimal times
to provide gentle nudges and task suggestions.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Optional, Callable
import threading
import time
import requests
import os
from datetime import datetime, timedelta


class PopupType:
    GENTLE_NUDGE = "gentle_nudge"
    TASK_SUGGESTION = "task_suggestion"
    BREAK_REMINDER = "break_reminder"
    PROGRESS_CELEBRATION = "progress_celebration"
    FOCUS_REMINDER = "focus_reminder"


class PopupManager:
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8010/api/v1")
        self.active_popups = []
        self.popup_history = []
        self.settings = {
            "enabled": True,
            "gentle_mode": True,
            "min_interval_minutes": 15,
            "max_popups_per_hour": 4,
            "quiet_hours_start": 22,  # 10 PM
            "quiet_hours_end": 8,     # 8 AM
            "do_not_disturb": False
        }
        
    def is_quiet_time(self) -> bool:
        """Check if it's currently quiet hours"""
        now = datetime.now()
        hour = now.hour
        
        start = self.settings["quiet_hours_start"]
        end = self.settings["quiet_hours_end"]
        
        if start > end:  # Overnight quiet hours (e.g., 22 to 8)
            return hour >= start or hour < end
        else:  # Same day quiet hours
            return start <= hour < end
    
    def can_show_popup(self) -> bool:
        """Check if we can show a popup now"""
        if not self.settings["enabled"] or self.settings["do_not_disturb"]:
            return False
            
        if self.is_quiet_time():
            return False
        
        # Check frequency limits
        now = datetime.now()
        recent_popups = [
            p for p in self.popup_history 
            if (now - p["timestamp"]).total_seconds() < 3600  # Last hour
        ]
        
        if len(recent_popups) >= self.settings["max_popups_per_hour"]:
            return False
        
        # Check minimum interval
        if self.popup_history:
            last_popup = max(self.popup_history, key=lambda x: x["timestamp"])
            minutes_since_last = (now - last_popup["timestamp"]).total_seconds() / 60
            if minutes_since_last < self.settings["min_interval_minutes"]:
                return False
        
        return True
    
    def show_gentle_nudge(self, idle_minutes: int, suggestion: str = None):
        """Show a gentle nudge popup after idle time"""
        if not self.can_show_popup():
            return
            
        if not suggestion:
            suggestion = self.get_contextual_suggestion()
        
        popup = GentleNudgePopup(
            idle_minutes=idle_minutes,
            suggestion=suggestion,
            on_start=self.on_popup_start,
            on_snooze=self.on_popup_snooze,
            on_dismiss=self.on_popup_dismiss
        )
        
        self.active_popups.append(popup)
        popup.show()
    
    def show_task_suggestion(self, task_data: Dict):
        """Show a specific task suggestion popup"""
        if not self.can_show_popup():
            return
            
        popup = TaskSuggestionPopup(
            task_data=task_data,
            on_accept=self.on_task_accepted,
            on_postpone=self.on_task_postponed,
            on_dismiss=self.on_popup_dismiss
        )
        
        self.active_popups.append(popup)
        popup.show()
    
    def show_progress_celebration(self, completed_tasks: int):
        """Show a celebration popup for completed tasks"""
        if not self.can_show_popup():
            return
            
        popup = ProgressCelebrationPopup(
            completed_tasks=completed_tasks,
            on_continue=self.on_continue_working,
            on_take_break=self.on_take_break,
            on_dismiss=self.on_popup_dismiss
        )
        
        self.active_popups.append(popup)
        popup.show()
    
    def get_contextual_suggestion(self) -> str:
        """Get a contextual suggestion from the backend or use fallback"""
        try:
            response = requests.get(f"{self.api_base_url}/suggestions/contextual", timeout=3)
            if response.status_code == 200:
                return response.json().get("suggestion", "")
        except:
            pass
        
        # Fallback suggestions
        fallback_suggestions = [
            "Organize one drawer in your workshop",
            "Check if any tools need cleaning",
            "Water one plant in your garden",
            "Review your project notes for 5 minutes",
            "Sketch a quick idea for your next project",
            "Take a 5-minute walk around your property",
            "Sort through one pile of papers",
            "Update your project progress log"
        ]
        
        import random
        return random.choice(fallback_suggestions)
    
    # Event handlers
    def on_popup_start(self, popup_type: str, data: Dict):
        """Handle when user starts a suggested task"""
        self.log_popup_interaction(popup_type, "started", data)
        self.dismiss_active_popups()
    
    def on_popup_snooze(self, popup_type: str, minutes: int):
        """Handle when user snoozes a popup"""
        self.log_popup_interaction(popup_type, "snoozed", {"minutes": minutes})
        # Schedule to show again later
        threading.Timer(minutes * 60, self.show_snoozed_popup).start()
    
    def on_popup_dismiss(self, popup_type: str):
        """Handle when user dismisses a popup"""
        self.log_popup_interaction(popup_type, "dismissed", {})
    
    def on_task_accepted(self, task_data: Dict):
        """Handle when user accepts a task suggestion"""
        self.log_popup_interaction("task_suggestion", "accepted", task_data)
        # Could integrate with backend to start task timer
    
    def on_task_postponed(self, task_data: Dict, minutes: int):
        """Handle when user postpones a task"""
        self.log_popup_interaction("task_suggestion", "postponed", {
            "task": task_data,
            "postpone_minutes": minutes
        })
    
    def on_continue_working(self):
        """Handle when user chooses to continue working"""
        self.log_popup_interaction("progress_celebration", "continue_working", {})
    
    def on_take_break(self, break_minutes: int):
        """Handle when user chooses to take a break"""
        self.log_popup_interaction("progress_celebration", "take_break", {
            "break_minutes": break_minutes
        })
    
    def log_popup_interaction(self, popup_type: str, action: str, data: Dict):
        """Log popup interaction for learning user preferences"""
        interaction = {
            "timestamp": datetime.now(),
            "popup_type": popup_type,
            "action": action,
            "data": data
        }
        
        self.popup_history.append(interaction)
        
        # Keep only last 100 interactions
        if len(self.popup_history) > 100:
            self.popup_history = self.popup_history[-100:]
    
    def dismiss_active_popups(self):
        """Dismiss all currently active popups"""
        for popup in self.active_popups:
            popup.dismiss()
        self.active_popups.clear()
    
    def show_snoozed_popup(self):
        """Show a snoozed popup (placeholder for now)"""
        # This would re-show the snoozed content
        pass
    
    def toggle_do_not_disturb(self, enabled: bool):
        """Toggle do not disturb mode"""
        self.settings["do_not_disturb"] = enabled
        if enabled:
            self.dismiss_active_popups()


class BasePopup:
    """Base class for all popup windows"""
    
    def __init__(self, title: str, on_dismiss: Callable = None):
        self.title = title
        self.on_dismiss = on_dismiss
        self.window = None
        self.dismissed = False
    
    def create_window(self, width: int = 400, height: int = 200):
        """Create the popup window"""
        self.window = ctk.CTkToplevel()
        self.window.title(self.title)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)
        
        # Center on screen
        self.center_window(width, height)
        
        # Always on top
        self.window.attributes("-topmost", True)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.dismiss)
        
        return self.window
    
    def center_window(self, width: int, height: int):
        """Center the window on screen"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self):
        """Show the popup window"""
        if not self.window:
            self.create_content()
        self.window.deiconify()
        self.window.focus_force()
    
    def dismiss(self):
        """Dismiss the popup window"""
        if self.dismissed:
            return
            
        self.dismissed = True
        
        if self.window:
            self.window.destroy()
        
        if self.on_dismiss:
            self.on_dismiss(self.__class__.__name__)
    
    def create_content(self):
        """Override in subclasses to create specific content"""
        pass


class GentleNudgePopup(BasePopup):
    """Gentle nudge popup for idle time suggestions"""
    
    def __init__(self, idle_minutes: int, suggestion: str, 
                 on_start: Callable = None, on_snooze: Callable = None, 
                 on_dismiss: Callable = None):
        super().__init__("🌟 Gentle Nudge", on_dismiss)
        self.idle_minutes = idle_minutes
        self.suggestion = suggestion
        self.on_start = on_start
        self.on_snooze = on_snooze
        
    def create_content(self):
        """Create the gentle nudge popup content"""
        self.create_window(450, 280)
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(header_frame, text="🌟", font=ctk.CTkFont(size=32))
        icon_label.pack()
        
        title_label = ctk.CTkLabel(header_frame, text="Gentle Nudge", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(5, 0))
        
        # Content
        content_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        idle_text = f"You've been idle for {self.idle_minutes} minutes"
        idle_label = ctk.CTkLabel(content_frame, text=idle_text, 
                                 font=ctk.CTkFont(size=14))
        idle_label.pack(pady=(0, 10))
        
        suggestion_label = ctk.CTkLabel(content_frame, text="Quick 5-minute task suggestion:",
                                       font=ctk.CTkFont(size=12, weight="bold"))
        suggestion_label.pack()
        
        suggestion_text = ctk.CTkLabel(content_frame, text=f'"{self.suggestion}"',
                                      font=ctk.CTkFont(size=13), 
                                      wraplength=350)
        suggestion_text.pack(pady=(5, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        start_btn = ctk.CTkButton(button_frame, text="✓ Start Now", 
                                 command=self.start_task, height=35)
        start_btn.pack(side="left", padx=(0, 10))
        
        snooze_btn = ctk.CTkButton(button_frame, text="⏰ Remind in 15m", 
                                  command=self.snooze_task, height=35)
        snooze_btn.pack(side="left", padx=5)
        
        dismiss_btn = ctk.CTkButton(button_frame, text="✗", width=40,
                                   command=self.dismiss, height=35)
        dismiss_btn.pack(side="right")
    
    def start_task(self):
        """Handle start task button"""
        if self.on_start:
            self.on_start(PopupType.GENTLE_NUDGE, {"suggestion": self.suggestion})
        self.dismiss()
    
    def snooze_task(self):
        """Handle snooze button"""
        if self.on_snooze:
            self.on_snooze(PopupType.GENTLE_NUDGE, 15)
        self.dismiss()


class TaskSuggestionPopup(BasePopup):
    """Specific task suggestion popup"""
    
    def __init__(self, task_data: Dict, on_accept: Callable = None,
                 on_postpone: Callable = None, on_dismiss: Callable = None):
        super().__init__("📋 Task Suggestion", on_dismiss)
        self.task_data = task_data
        self.on_accept = on_accept
        self.on_postpone = on_postpone
    
    def create_content(self):
        """Create task suggestion popup content"""
        self.create_window(500, 320)
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(header_frame, text="📋", font=ctk.CTkFont(size=32))
        icon_label.pack()
        
        title_label = ctk.CTkLabel(header_frame, text="Suggested Task", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(5, 0))
        
        # Task details
        task_frame = ctk.CTkFrame(self.window)
        task_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        task_title = self.task_data.get("title", "Unnamed Task")
        title_label = ctk.CTkLabel(task_frame, text=task_title,
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(15, 5))
        
        if "description" in self.task_data:
            desc_label = ctk.CTkLabel(task_frame, text=self.task_data["description"],
                                     font=ctk.CTkFont(size=12), wraplength=400)
            desc_label.pack(pady=(0, 10))
        
        estimated_time = self.task_data.get("estimated_minutes", 15)
        time_label = ctk.CTkLabel(task_frame, text=f"Estimated time: {estimated_time} minutes",
                                 font=ctk.CTkFont(size=12), text_color="gray")
        time_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        accept_btn = ctk.CTkButton(button_frame, text="✓ Start Task", 
                                  command=self.accept_task, height=35)
        accept_btn.pack(side="left", padx=(0, 10))
        
        postpone_btn = ctk.CTkButton(button_frame, text="⏰ Later", 
                                    command=self.postpone_task, height=35)
        postpone_btn.pack(side="left", padx=5)
        
        dismiss_btn = ctk.CTkButton(button_frame, text="✗", width=40,
                                   command=self.dismiss, height=35)
        dismiss_btn.pack(side="right")
    
    def accept_task(self):
        """Handle accept task button"""
        if self.on_accept:
            self.on_accept(self.task_data)
        self.dismiss()
    
    def postpone_task(self):
        """Handle postpone task button"""
        if self.on_postpone:
            self.on_postpone(self.task_data, 30)  # Postpone 30 minutes
        self.dismiss()


class ProgressCelebrationPopup(BasePopup):
    """Progress celebration popup"""
    
    def __init__(self, completed_tasks: int, on_continue: Callable = None,
                 on_take_break: Callable = None, on_dismiss: Callable = None):
        super().__init__("🎉 Great Progress!", on_dismiss)
        self.completed_tasks = completed_tasks
        self.on_continue = on_continue
        self.on_take_break = on_take_break
    
    def create_content(self):
        """Create celebration popup content"""
        self.create_window(400, 250)
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(header_frame, text="🎉", font=ctk.CTkFont(size=32))
        icon_label.pack()
        
        title_label = ctk.CTkLabel(header_frame, text="Great Progress!", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(5, 0))
        
        # Content
        content_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        progress_text = f"You've completed {self.completed_tasks} tasks today!"
        progress_label = ctk.CTkLabel(content_frame, text=progress_text,
                                     font=ctk.CTkFont(size=14))
        progress_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        continue_btn = ctk.CTkButton(button_frame, text="🚀 Keep Going", 
                                    command=self.continue_working, height=35)
        continue_btn.pack(side="left", padx=(0, 10))
        
        break_btn = ctk.CTkButton(button_frame, text="☕ Take Break", 
                                 command=self.take_break, height=35)
        break_btn.pack(side="left", padx=5)
        
        dismiss_btn = ctk.CTkButton(button_frame, text="✗", width=40,
                                   command=self.dismiss, height=35)
        dismiss_btn.pack(side="right")
    
    def continue_working(self):
        """Handle continue working button"""
        if self.on_continue:
            self.on_continue()
        self.dismiss()
    
    def take_break(self):
        """Handle take break button"""
        if self.on_take_break:
            self.on_take_break(15)  # 15 minute break
        self.dismiss()


# Global popup manager instance
_popup_manager = None

def get_popup_manager() -> PopupManager:
    """Get the global popup manager instance"""
    global _popup_manager
    if _popup_manager is None:
        _popup_manager = PopupManager()
    return _popup_manager 
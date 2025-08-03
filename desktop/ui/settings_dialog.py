"""
Settings Dialog for Motivate.AI

Provides a comprehensive settings interface for configuring the application,
including API settings, appearance, notifications, and other preferences.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Optional, Callable
import os
import json
import threading
import requests
from pathlib import Path
from .theme_manager import get_color, get_button_colors, apply_theme_change, ThemeMode, register_theme_change_callback


class SettingsDialog:
    def __init__(self, parent, on_settings_saved: Callable = None):
        self.parent = parent
        self.on_settings_saved = on_settings_saved
        self.window = None
        self.settings_file = Path.home() / ".motivate_ai" / "settings.json"
        self.settings = self.load_settings()
        
        # Register for theme changes to update dialog colors
        register_theme_change_callback(self._on_theme_changed)
        
    def load_settings(self) -> Dict:
        """Load settings from file or return defaults"""
        default_settings = {
            "api": {
                "base_url": "http://127.0.0.1:8010/api/v1",
                "timeout": 10,
                "auto_connect": True
            },
            "appearance": {
                "theme": "system",  # "light", "dark", "system"
                "color_theme": "blue",
                "font_size": "normal",  # "small", "normal", "large"
                "sidebar_width": 620,
                "task_detail_width": 450
            },
            "notifications": {
                "enabled": True,
                "task_reminders": True,
                "ai_status_alerts": True,
                "sound_enabled": False
            },
            "behavior": {
                "auto_save": True,
                "confirm_deletions": True,
                "show_tooltips": True,
                "start_minimized": False
            },
            "ai": {
                "auto_check_status": True,
                "show_ai_suggestions": True,
                "ai_timeout": 30
            }
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults to handle missing keys
                    return self.merge_settings(default_settings, saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def merge_settings(self, defaults: Dict, saved: Dict) -> Dict:
        """Recursively merge saved settings with defaults"""
        result = defaults.copy()
        for key, value in saved.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            # Update environment variables
            os.environ["API_BASE_URL"] = self.settings["api"]["base_url"]
            
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def show(self):
        """Show the settings dialog"""
        if self.window and self.window.winfo_exists():
            self.window.focus_force()
            self.window.lift()
            return
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the settings dialog window with dynamic sizing"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Settings - Motivate.AI")
        
        # Calculate dynamic window size based on screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Use 60% of screen width, 80% of screen height (with reasonable bounds)
        window_width = max(800, min(1200, int(screen_width * 0.6)))
        window_height = max(700, min(1000, int(screen_height * 0.8)))
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.minsize(750, 650)
        self.window.resizable(True, True)
        
        # Center on screen
        self.window.update_idletasks()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ensure window appears in front
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.attributes('-topmost', True)
        self.window.after(100, lambda: self.window.attributes('-topmost', False))
        
        # Handle close
        self.window.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        # Create content
        self.create_content()
    
    def create_content(self):
        """Create the settings content with scrollable tabs"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header (fixed at top)
        header_frame = ctk.CTkFrame(main_container, height=70, fg_color=get_color("surface_primary"))
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="⚙️ Settings", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Scrollable content area
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Tab view inside scrollable area
        self.tab_view = ctk.CTkTabview(content_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs (Appearance first)
        self.create_appearance_tab()
        self.create_api_tab()
        self.create_notifications_tab()
        self.create_behavior_tab()
        self.create_ai_tab()
        
        # Buttons (fixed at bottom)
        self.create_buttons(main_container)
    
    def create_api_tab(self):
        """Create API settings tab with scrollable content"""
        api_tab = self.tab_view.add("API")
        
        # Make the tab content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(api_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        content_container = scrollable_frame
        
        # API Base URL
        ctk.CTkLabel(content_container, text="API Configuration", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Base URL
        ctk.CTkLabel(content_container, text="API Base URL:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.api_url_entry = ctk.CTkEntry(content_container, height=40,
                                         placeholder_text="http://127.0.0.1:8010/api/v1",
                                         font=ctk.CTkFont(size=14))
        self.api_url_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.api_url_entry.insert(0, self.settings["api"]["base_url"])
        
        # Test connection button
        test_frame = ctk.CTkFrame(content_container, fg_color=get_color("surface_transparent"))
        test_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.test_btn = ctk.CTkButton(test_frame, text="Test Connection", 
                                     command=self.test_api_connection,
                                     height=40, width=140, font=ctk.CTkFont(size=14))
        self.test_btn.pack(side="left")
        
        self.connection_status = ctk.CTkLabel(test_frame, text="", 
                                             font=ctk.CTkFont(size=14))
        self.connection_status.pack(side="left", padx=(10, 0))
        
        # Timeout
        ctk.CTkLabel(content_container, text="Request Timeout (seconds):", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.timeout_var = tk.StringVar(value=str(self.settings["api"]["timeout"]))
        self.timeout_entry = ctk.CTkEntry(content_container, height=40, textvariable=self.timeout_var,
                                         font=ctk.CTkFont(size=14))
        self.timeout_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Auto connect
        self.auto_connect_var = tk.BooleanVar(value=self.settings["api"]["auto_connect"])
        auto_connect_check = ctk.CTkCheckBox(content_container, text="Auto-connect on startup",
                                           variable=self.auto_connect_var,
                                           font=ctk.CTkFont(size=15))
        auto_connect_check.pack(anchor="w", padx=20, pady=(0, 30))
    
    def create_appearance_tab(self):
        """Create appearance settings tab with scrollable content"""
        appearance_tab = self.tab_view.add("Appearance")
        
        # Make the tab content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(appearance_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Use scrollable_frame instead of appearance_tab for content
        content_container = scrollable_frame
        
        ctk.CTkLabel(content_container, text="Theme Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Dark Mode Toggle Switch
        theme_frame = ctk.CTkFrame(content_container, fg_color=get_color("surface_secondary"))
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(theme_frame, text="Dark Mode:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Determine initial switch state based on current theme
        current_theme = self.settings["appearance"]["theme"]
        initial_dark_mode = current_theme == "dark"
        
        self.dark_mode_var = tk.BooleanVar(value=initial_dark_mode)
        self.dark_mode_switch = ctk.CTkSwitch(theme_frame, 
                                             text="Enable dark mode",
                                             variable=self.dark_mode_var,
                                             font=ctk.CTkFont(size=15),
                                             command=self._on_dark_mode_toggle)
        self.dark_mode_switch.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Color theme
        ctk.CTkLabel(content_container, text="Color Theme:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.color_theme_var = tk.StringVar(value=self.settings["appearance"]["color_theme"])
        color_combo = ctk.CTkComboBox(content_container, values=["blue", "green", "dark-blue"],
                                     variable=self.color_theme_var, height=40,
                                     font=ctk.CTkFont(size=15), command=self._on_color_theme_changed)
        color_combo.pack(fill="x", padx=20, pady=(0, 15))
        
        # Font size
        ctk.CTkLabel(content_container, text="Font Size:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.font_size_var = tk.StringVar(value=self.settings["appearance"]["font_size"])
        font_combo = ctk.CTkComboBox(content_container, values=["small", "normal", "large"],
                                    variable=self.font_size_var, height=40,
                                    font=ctk.CTkFont(size=15), command=self._on_font_size_changed)
        font_combo.pack(fill="x", padx=20, pady=(0, 15))
        
        # Layout settings
        ctk.CTkLabel(content_container, text="Layout Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Sidebar width
        ctk.CTkLabel(content_container, text="Sidebar Width (pixels):", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.sidebar_width_var = tk.StringVar(value=str(self.settings["appearance"]["sidebar_width"]))
        sidebar_width_entry = ctk.CTkEntry(content_container, height=40, textvariable=self.sidebar_width_var,
                                          font=ctk.CTkFont(size=15))
        sidebar_width_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Task detail width
        ctk.CTkLabel(content_container, text="Task Detail Width (pixels):", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.task_detail_width_var = tk.StringVar(value=str(self.settings["appearance"]["task_detail_width"]))
        task_detail_width_entry = ctk.CTkEntry(content_container, height=40, textvariable=self.task_detail_width_var,
                                              font=ctk.CTkFont(size=15))
        task_detail_width_entry.pack(fill="x", padx=20, pady=(0, 30))  # Extra bottom padding for scrolling
    
    def create_notifications_tab(self):
        """Create notifications settings tab with scrollable content"""
        notifications_tab = self.tab_view.add("Notifications")
        
        # Make the tab content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(notifications_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        content_container = scrollable_frame
        
        ctk.CTkLabel(content_container, text="Notification Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Enable notifications
        self.notifications_enabled_var = tk.BooleanVar(value=self.settings["notifications"]["enabled"])
        notifications_check = ctk.CTkCheckBox(content_container, text="Enable notifications",
                                            variable=self.notifications_enabled_var,
                                            font=ctk.CTkFont(size=15), command=self._on_notifications_toggled)
        notifications_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Task reminders
        self.task_reminders_var = tk.BooleanVar(value=self.settings["notifications"]["task_reminders"])
        task_reminders_check = ctk.CTkCheckBox(content_container, text="Task reminders",
                                              variable=self.task_reminders_var,
                                              font=ctk.CTkFont(size=15))
        task_reminders_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # AI status alerts
        self.ai_alerts_var = tk.BooleanVar(value=self.settings["notifications"]["ai_status_alerts"])
        ai_alerts_check = ctk.CTkCheckBox(content_container, text="AI status alerts",
                                         variable=self.ai_alerts_var,
                                         font=ctk.CTkFont(size=15))
        ai_alerts_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Sound
        self.sound_enabled_var = tk.BooleanVar(value=self.settings["notifications"]["sound_enabled"])
        sound_check = ctk.CTkCheckBox(content_container, text="Enable sound notifications",
                                     variable=self.sound_enabled_var,
                                     font=ctk.CTkFont(size=15))
        sound_check.pack(anchor="w", padx=20, pady=(0, 30))
    
    def create_behavior_tab(self):
        """Create behavior settings tab with scrollable content"""
        behavior_tab = self.tab_view.add("Behavior")
        
        # Make the tab content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(behavior_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        content_container = scrollable_frame
        
        ctk.CTkLabel(content_container, text="Application Behavior", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Auto save
        self.auto_save_var = tk.BooleanVar(value=self.settings["behavior"]["auto_save"])
        auto_save_check = ctk.CTkCheckBox(content_container, text="Auto-save changes",
                                         variable=self.auto_save_var,
                                         font=ctk.CTkFont(size=15))
        auto_save_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Confirm deletions
        self.confirm_deletions_var = tk.BooleanVar(value=self.settings["behavior"]["confirm_deletions"])
        confirm_deletions_check = ctk.CTkCheckBox(content_container, text="Confirm deletions",
                                                 variable=self.confirm_deletions_var,
                                                 font=ctk.CTkFont(size=15))
        confirm_deletions_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Show tooltips
        self.show_tooltips_var = tk.BooleanVar(value=self.settings["behavior"]["show_tooltips"])
        tooltips_check = ctk.CTkCheckBox(content_container, text="Show tooltips",
                                        variable=self.show_tooltips_var,
                                        font=ctk.CTkFont(size=15))
        tooltips_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Start minimized
        self.start_minimized_var = tk.BooleanVar(value=self.settings["behavior"]["start_minimized"])
        start_minimized_check = ctk.CTkCheckBox(content_container, text="Start minimized to system tray",
                                               variable=self.start_minimized_var,
                                               font=ctk.CTkFont(size=15))
        start_minimized_check.pack(anchor="w", padx=20, pady=(0, 30))
    
    def create_ai_tab(self):
        """Create AI settings tab with scrollable content"""
        ai_tab = self.tab_view.add("AI")
        
        # Make the tab content scrollable
        scrollable_frame = ctk.CTkScrollableFrame(ai_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        content_container = scrollable_frame
        
        ctk.CTkLabel(content_container, text="AI Assistant Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Auto check status
        self.auto_check_ai_var = tk.BooleanVar(value=self.settings["ai"]["auto_check_status"])
        auto_check_check = ctk.CTkCheckBox(content_container, text="Auto-check AI status",
                                          variable=self.auto_check_ai_var,
                                          font=ctk.CTkFont(size=15))
        auto_check_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Show AI suggestions
        self.show_ai_suggestions_var = tk.BooleanVar(value=self.settings["ai"]["show_ai_suggestions"])
        ai_suggestions_check = ctk.CTkCheckBox(content_container, text="Show AI suggestions",
                                              variable=self.show_ai_suggestions_var,
                                              font=ctk.CTkFont(size=15))
        ai_suggestions_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # AI timeout
        ctk.CTkLabel(content_container, text="AI Request Timeout (seconds):", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.ai_timeout_var = tk.StringVar(value=str(self.settings["ai"]["ai_timeout"]))
        ai_timeout_entry = ctk.CTkEntry(content_container, height=40, textvariable=self.ai_timeout_var,
                                       font=ctk.CTkFont(size=15))
        ai_timeout_entry.pack(fill="x", padx=20, pady=(0, 30))
    
    def create_buttons(self, parent):
        """Create the bottom buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color=get_color("surface_secondary"))
        button_frame.pack(fill="x", pady=(0, 0))
        
        btn_container = ctk.CTkFrame(button_frame, fg_color=get_color("surface_transparent"))
        btn_container.pack(pady=15, padx=20)
        
        # Save button
        save_colors = get_button_colors("success")
        ctk.CTkButton(btn_container, text="💾 Save Settings", command=self.save_and_close,
                     height=45, width=140, font=ctk.CTkFont(size=15, weight="bold"),
                     **save_colors
                     ).pack(side="left", padx=(0, 10))
        
        # Apply button
        apply_colors = get_button_colors("primary")
        ctk.CTkButton(btn_container, text="Apply", command=self.apply_settings,
                     height=45, width=100, font=ctk.CTkFont(size=14),
                     **apply_colors
                     ).pack(side="left", padx=(0, 10))
        
        # Reset button
        reset_colors = get_button_colors("warning")
        ctk.CTkButton(btn_container, text="Reset to Defaults", command=self.reset_settings,
                     height=45, width=140, font=ctk.CTkFont(size=14),
                     **reset_colors
                     ).pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_colors = get_button_colors("secondary")
        ctk.CTkButton(btn_container, text="Cancel", command=self.close_dialog,
                     height=45, width=100, font=ctk.CTkFont(size=14),
                     **cancel_colors
                     ).pack(side="left")
    
    def test_api_connection(self):
        """Test the API connection"""
        self.test_btn.configure(state="disabled", text="Testing...")
        self.connection_status.configure(text="", text_color=get_color("text_primary"))
        
        def test_connection():
            try:
                url = self.api_url_entry.get().strip()
                if not url:
                    self.connection_status.configure(text="Please enter a URL", text_color=get_color("text_error"))
                    return
                
                response = requests.get(f"{url}/projects", timeout=5)
                if response.status_code == 200:
                    self.connection_status.configure(text="✓ Connected successfully", text_color=get_color("text_success"))
                else:
                    self.connection_status.configure(text=f"✗ HTTP {response.status_code}", text_color=get_color("text_error"))
            except requests.exceptions.ConnectionError:
                self.connection_status.configure(text="✗ Connection failed", text_color=get_color("text_error"))
            except requests.exceptions.Timeout:
                self.connection_status.configure(text="✗ Timeout", text_color=get_color("text_error"))
            except Exception as e:
                self.connection_status.configure(text=f"✗ Error: {str(e)}", text_color=get_color("text_error"))
            finally:
                self.test_btn.configure(state="normal", text="Test Connection")
        
        thread = threading.Thread(target=test_connection, daemon=True)
        thread.start()
    
    def collect_settings(self):
        """Collect all settings from the UI"""
        try:
            self.settings["api"]["base_url"] = self.api_url_entry.get().strip()
            self.settings["api"]["timeout"] = int(self.timeout_var.get())
            self.settings["api"]["auto_connect"] = self.auto_connect_var.get()
            
            # Handle dark mode toggle
            self.settings["appearance"]["theme"] = "dark" if self.dark_mode_var.get() else "light"
            self.settings["appearance"]["color_theme"] = self.color_theme_var.get()
            self.settings["appearance"]["font_size"] = self.font_size_var.get()
            self.settings["appearance"]["sidebar_width"] = int(self.sidebar_width_var.get())
            self.settings["appearance"]["task_detail_width"] = int(self.task_detail_width_var.get())
            
            self.settings["notifications"]["enabled"] = self.notifications_enabled_var.get()
            self.settings["notifications"]["task_reminders"] = self.task_reminders_var.get()
            self.settings["notifications"]["ai_status_alerts"] = self.ai_alerts_var.get()
            self.settings["notifications"]["sound_enabled"] = self.sound_enabled_var.get()
            
            self.settings["behavior"]["auto_save"] = self.auto_save_var.get()
            self.settings["behavior"]["confirm_deletions"] = self.confirm_deletions_var.get()
            self.settings["behavior"]["show_tooltips"] = self.show_tooltips_var.get()
            self.settings["behavior"]["start_minimized"] = self.start_minimized_var.get()
            
            self.settings["ai"]["auto_check_status"] = self.auto_check_ai_var.get()
            self.settings["ai"]["show_ai_suggestions"] = self.show_ai_suggestions_var.get()
            self.settings["ai"]["ai_timeout"] = int(self.ai_timeout_var.get())
            
            return True
        except ValueError as e:
            print(f"Error collecting settings: {e}")
            return False
    
    def apply_settings(self):
        """Apply settings without closing"""
        if self.collect_settings():
            if self.save_settings():
                # Update appearance if needed
                theme = self.settings["appearance"]["theme"]
                if theme != "system":
                    ctk.set_appearance_mode(theme)
                
                color_theme = self.settings["appearance"]["color_theme"]
                ctk.set_default_color_theme(color_theme)
                
                if self.on_settings_saved:
                    self.on_settings_saved(self.settings)
                
                # Show success message
                self.show_success_message("Settings applied successfully!")
                return True
            else:
                self.show_error_message("Failed to save settings!")
                return False
        else:
            self.show_error_message("Invalid settings values!")
            return False
    
    def save_and_close(self):
        """Save settings and close dialog"""
        if self.apply_settings():
            self.close_dialog()
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        # Reload default settings
        self.settings = self.load_settings()
        
        # Update UI with default values
        self.api_url_entry.delete(0, 'end')
        self.api_url_entry.insert(0, self.settings["api"]["base_url"])
        
        self.timeout_var.set(str(self.settings["api"]["timeout"]))
        self.auto_connect_var.set(self.settings["api"]["auto_connect"])
        
        # Update dark mode switch based on theme
        current_theme = self.settings["appearance"]["theme"]
        self.dark_mode_var.set(current_theme == "dark")
        self.color_theme_var.set(self.settings["appearance"]["color_theme"])
        self.font_size_var.set(self.settings["appearance"]["font_size"])
        self.sidebar_width_var.set(str(self.settings["appearance"]["sidebar_width"]))
        self.task_detail_width_var.set(str(self.settings["appearance"]["task_detail_width"]))
        
        self.notifications_enabled_var.set(self.settings["notifications"]["enabled"])
        self.task_reminders_var.set(self.settings["notifications"]["task_reminders"])
        self.ai_alerts_var.set(self.settings["notifications"]["ai_status_alerts"])
        self.sound_enabled_var.set(self.settings["notifications"]["sound_enabled"])
        
        self.auto_save_var.set(self.settings["behavior"]["auto_save"])
        self.confirm_deletions_var.set(self.settings["behavior"]["confirm_deletions"])
        self.show_tooltips_var.set(self.settings["behavior"]["show_tooltips"])
        self.start_minimized_var.set(self.settings["behavior"]["start_minimized"])
        
        self.auto_check_ai_var.set(self.settings["ai"]["auto_check_status"])
        self.show_ai_suggestions_var.set(self.settings["ai"]["show_ai_suggestions"])
        self.ai_timeout_var.set(str(self.settings["ai"]["ai_timeout"]))
        
        self.show_success_message("Settings reset to defaults!")
    
    def _on_dark_mode_toggle(self):
        """Handle dark mode toggle switch"""
        try:
            # Convert boolean to theme mode
            if self.dark_mode_var.get():
                mode = ThemeMode.DARK
                theme_value = "dark"
            else:
                mode = ThemeMode.LIGHT
                theme_value = "light"
            
            # Apply theme change immediately for preview
            apply_theme_change(mode)
            
            # Save the setting immediately
            self.settings["appearance"]["theme"] = theme_value
            self.save_settings()
            
            # Notify that settings were saved
            if self.on_settings_saved:
                self.on_settings_saved(self.settings)
                
        except Exception as e:
            print(f"Error toggling dark mode: {e}")
    
    def _on_color_theme_changed(self, value):
        """Handle color theme change"""
        try:
            # Update the setting immediately
            self.settings["appearance"]["color_theme"] = value
            
            # Apply the color theme
            ctk.set_default_color_theme(value)
            
            # Save the setting
            self.save_settings()
            
            # Notify that settings were saved
            if self.on_settings_saved:
                self.on_settings_saved(self.settings)
                
        except Exception as e:
            print(f"Error changing color theme: {e}")
    
    def _on_font_size_changed(self, value):
        """Handle font size change"""
        try:
            # Update the setting immediately
            self.settings["appearance"]["font_size"] = value
            
            # Save the setting
            self.save_settings()
            
            # Notify that settings were saved
            if self.on_settings_saved:
                self.on_settings_saved(self.settings)
                
        except Exception as e:
            print(f"Error changing font size: {e}")
    
    def _on_notifications_toggled(self):
        """Handle notifications toggle"""
        try:
            # Update the setting immediately
            self.settings["notifications"]["enabled"] = self.notifications_enabled_var.get()
            
            # Save the setting
            self.save_settings()
            
            # Notify that settings were saved
            if self.on_settings_saved:
                self.on_settings_saved(self.settings)
                
        except Exception as e:
            print(f"Error toggling notifications: {e}")
    
    def show_success_message(self, message: str):
        """Show a temporary success message"""
        # Create a temporary label
        if hasattr(self, 'temp_message'):
            self.temp_message.destroy()
        
        self.temp_message = ctk.CTkLabel(self.window, text=message, 
                                        font=ctk.CTkFont(size=14),
                                        text_color=get_color("text_success"))
        self.temp_message.pack(pady=5)
        
        # Remove after 3 seconds
        self.window.after(3000, lambda: self.temp_message.destroy() if hasattr(self, 'temp_message') else None)
    
    def show_error_message(self, message: str):
        """Show a temporary error message"""
        # Create a temporary label
        if hasattr(self, 'temp_message'):
            self.temp_message.destroy()
        
        self.temp_message = ctk.CTkLabel(self.window, text=message, 
                                        font=ctk.CTkFont(size=14),
                                        text_color=get_color("text_error"))
        self.temp_message.pack(pady=5)
        
        # Remove after 3 seconds
        self.window.after(3000, lambda: self.temp_message.destroy() if hasattr(self, 'temp_message') else None)
    
    # Remove old theme preview method since we're using the dark mode toggle now
    
    def _on_theme_changed(self):
        """Handle theme changes - update dialog colors"""
        if self.window and self.window.winfo_exists():
            # This will be called when theme changes to update the dialog
            pass  # Colors are already using get_color() so they'll update automatically
    
    def close_dialog(self):
        """Close the settings dialog"""
        if self.window:
            self.window.destroy()
            self.window = None


# Global settings dialog instance
_settings_dialog = None

def show_settings_dialog(parent, on_settings_saved: Callable = None):
    """Show the settings dialog (reuses existing instance)"""
    global _settings_dialog
    
    if _settings_dialog is None:
        _settings_dialog = SettingsDialog(parent, on_settings_saved)
    else:
        _settings_dialog.on_settings_saved = on_settings_saved
    
    _settings_dialog.show()

def get_settings_dialog() -> SettingsDialog:
    """Get the current settings dialog instance"""
    return _settings_dialog

if __name__ == "__main__":
    # Test the settings dialog
    app = ctk.CTk()
    app.withdraw()  # Hide main window
    
    def on_settings_saved(settings):
        print(f"Settings saved: {settings}")
    
    show_settings_dialog(app, on_settings_saved)
    
    app.mainloop() 
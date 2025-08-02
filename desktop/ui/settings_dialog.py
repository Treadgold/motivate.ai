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


class SettingsDialog:
    def __init__(self, parent, on_settings_saved: Callable = None):
        self.parent = parent
        self.on_settings_saved = on_settings_saved
        self.window = None
        self.settings_file = Path.home() / ".motivate_ai" / "settings.json"
        self.settings = self.load_settings()
        
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
        """Create the settings dialog window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Settings - Motivate.AI")
        self.window.geometry("800x600")
        self.window.minsize(700, 500)
        self.window.resizable(True, True)
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 800) // 2
        y = (self.window.winfo_screenheight() - 600) // 2
        self.window.geometry(f"800x600+{x}+{y}")
        
        # Handle close
        self.window.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        # Create content
        self.create_content()
    
    def create_content(self):
        """Create the settings content with tabs"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, height=60, fg_color=("gray90", "gray10"))
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, text="⚙️ Settings", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=15)
        
        # Tab view
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create tabs
        self.create_api_tab()
        self.create_appearance_tab()
        self.create_notifications_tab()
        self.create_behavior_tab()
        self.create_ai_tab()
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_api_tab(self):
        """Create API settings tab"""
        api_tab = self.tab_view.add("API")
        
        # API Base URL
        ctk.CTkLabel(api_tab, text="API Configuration", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Base URL
        ctk.CTkLabel(api_tab, text="API Base URL:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.api_url_entry = ctk.CTkEntry(api_tab, height=35,
                                         placeholder_text="http://127.0.0.1:8010/api/v1",
                                         font=ctk.CTkFont(size=13))
        self.api_url_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.api_url_entry.insert(0, self.settings["api"]["base_url"])
        
        # Test connection button
        test_frame = ctk.CTkFrame(api_tab, fg_color="transparent")
        test_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.test_btn = ctk.CTkButton(test_frame, text="Test Connection", 
                                     command=self.test_api_connection,
                                     height=35, width=120)
        self.test_btn.pack(side="left")
        
        self.connection_status = ctk.CTkLabel(test_frame, text="", 
                                             font=ctk.CTkFont(size=12))
        self.connection_status.pack(side="left", padx=(10, 0))
        
        # Timeout
        ctk.CTkLabel(api_tab, text="Request Timeout (seconds):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.timeout_var = tk.StringVar(value=str(self.settings["api"]["timeout"]))
        self.timeout_entry = ctk.CTkEntry(api_tab, height=35, textvariable=self.timeout_var,
                                         font=ctk.CTkFont(size=13))
        self.timeout_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Auto connect
        self.auto_connect_var = tk.BooleanVar(value=self.settings["api"]["auto_connect"])
        auto_connect_check = ctk.CTkCheckBox(api_tab, text="Auto-connect on startup",
                                           variable=self.auto_connect_var,
                                           font=ctk.CTkFont(size=13))
        auto_connect_check.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        appearance_tab = self.tab_view.add("Appearance")
        
        ctk.CTkLabel(appearance_tab, text="Visual Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Theme
        ctk.CTkLabel(appearance_tab, text="Theme:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.theme_var = tk.StringVar(value=self.settings["appearance"]["theme"])
        theme_combo = ctk.CTkComboBox(appearance_tab, values=["light", "dark", "system"],
                                     variable=self.theme_var, height=35,
                                     font=ctk.CTkFont(size=13))
        theme_combo.pack(fill="x", padx=20, pady=(0, 10))
        
        # Color theme
        ctk.CTkLabel(appearance_tab, text="Color Theme:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.color_theme_var = tk.StringVar(value=self.settings["appearance"]["color_theme"])
        color_combo = ctk.CTkComboBox(appearance_tab, values=["blue", "green", "dark-blue"],
                                     variable=self.color_theme_var, height=35,
                                     font=ctk.CTkFont(size=13))
        color_combo.pack(fill="x", padx=20, pady=(0, 10))
        
        # Font size
        ctk.CTkLabel(appearance_tab, text="Font Size:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.font_size_var = tk.StringVar(value=self.settings["appearance"]["font_size"])
        font_combo = ctk.CTkComboBox(appearance_tab, values=["small", "normal", "large"],
                                    variable=self.font_size_var, height=35,
                                    font=ctk.CTkFont(size=13))
        font_combo.pack(fill="x", padx=20, pady=(0, 10))
        
        # Layout settings
        ctk.CTkLabel(appearance_tab, text="Layout Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Sidebar width
        ctk.CTkLabel(appearance_tab, text="Sidebar Width (pixels):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.sidebar_width_var = tk.StringVar(value=str(self.settings["appearance"]["sidebar_width"]))
        sidebar_width_entry = ctk.CTkEntry(appearance_tab, height=35, textvariable=self.sidebar_width_var,
                                          font=ctk.CTkFont(size=13))
        sidebar_width_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Task detail width
        ctk.CTkLabel(appearance_tab, text="Task Detail Width (pixels):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.task_detail_width_var = tk.StringVar(value=str(self.settings["appearance"]["task_detail_width"]))
        task_detail_width_entry = ctk.CTkEntry(appearance_tab, height=35, textvariable=self.task_detail_width_var,
                                              font=ctk.CTkFont(size=13))
        task_detail_width_entry.pack(fill="x", padx=20, pady=(0, 20))
    
    def create_notifications_tab(self):
        """Create notifications settings tab"""
        notifications_tab = self.tab_view.add("Notifications")
        
        ctk.CTkLabel(notifications_tab, text="Notification Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Enable notifications
        self.notifications_enabled_var = tk.BooleanVar(value=self.settings["notifications"]["enabled"])
        notifications_check = ctk.CTkCheckBox(notifications_tab, text="Enable notifications",
                                            variable=self.notifications_enabled_var,
                                            font=ctk.CTkFont(size=13))
        notifications_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Task reminders
        self.task_reminders_var = tk.BooleanVar(value=self.settings["notifications"]["task_reminders"])
        task_reminders_check = ctk.CTkCheckBox(notifications_tab, text="Task reminders",
                                              variable=self.task_reminders_var,
                                              font=ctk.CTkFont(size=13))
        task_reminders_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # AI status alerts
        self.ai_alerts_var = tk.BooleanVar(value=self.settings["notifications"]["ai_status_alerts"])
        ai_alerts_check = ctk.CTkCheckBox(notifications_tab, text="AI status alerts",
                                         variable=self.ai_alerts_var,
                                         font=ctk.CTkFont(size=13))
        ai_alerts_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Sound
        self.sound_enabled_var = tk.BooleanVar(value=self.settings["notifications"]["sound_enabled"])
        sound_check = ctk.CTkCheckBox(notifications_tab, text="Enable sound notifications",
                                     variable=self.sound_enabled_var,
                                     font=ctk.CTkFont(size=13))
        sound_check.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_behavior_tab(self):
        """Create behavior settings tab"""
        behavior_tab = self.tab_view.add("Behavior")
        
        ctk.CTkLabel(behavior_tab, text="Application Behavior", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Auto save
        self.auto_save_var = tk.BooleanVar(value=self.settings["behavior"]["auto_save"])
        auto_save_check = ctk.CTkCheckBox(behavior_tab, text="Auto-save changes",
                                         variable=self.auto_save_var,
                                         font=ctk.CTkFont(size=13))
        auto_save_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Confirm deletions
        self.confirm_deletions_var = tk.BooleanVar(value=self.settings["behavior"]["confirm_deletions"])
        confirm_deletions_check = ctk.CTkCheckBox(behavior_tab, text="Confirm deletions",
                                                 variable=self.confirm_deletions_var,
                                                 font=ctk.CTkFont(size=13))
        confirm_deletions_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Show tooltips
        self.show_tooltips_var = tk.BooleanVar(value=self.settings["behavior"]["show_tooltips"])
        tooltips_check = ctk.CTkCheckBox(behavior_tab, text="Show tooltips",
                                        variable=self.show_tooltips_var,
                                        font=ctk.CTkFont(size=13))
        tooltips_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Start minimized
        self.start_minimized_var = tk.BooleanVar(value=self.settings["behavior"]["start_minimized"])
        start_minimized_check = ctk.CTkCheckBox(behavior_tab, text="Start minimized to system tray",
                                               variable=self.start_minimized_var,
                                               font=ctk.CTkFont(size=13))
        start_minimized_check.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_ai_tab(self):
        """Create AI settings tab"""
        ai_tab = self.tab_view.add("AI")
        
        ctk.CTkLabel(ai_tab, text="AI Assistant Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Auto check status
        self.auto_check_ai_var = tk.BooleanVar(value=self.settings["ai"]["auto_check_status"])
        auto_check_check = ctk.CTkCheckBox(ai_tab, text="Auto-check AI status",
                                          variable=self.auto_check_ai_var,
                                          font=ctk.CTkFont(size=13))
        auto_check_check.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Show AI suggestions
        self.show_ai_suggestions_var = tk.BooleanVar(value=self.settings["ai"]["show_ai_suggestions"])
        ai_suggestions_check = ctk.CTkCheckBox(ai_tab, text="Show AI suggestions",
                                              variable=self.show_ai_suggestions_var,
                                              font=ctk.CTkFont(size=13))
        ai_suggestions_check.pack(anchor="w", padx=20, pady=(0, 5))
        
        # AI timeout
        ctk.CTkLabel(ai_tab, text="AI Request Timeout (seconds):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.ai_timeout_var = tk.StringVar(value=str(self.settings["ai"]["ai_timeout"]))
        ai_timeout_entry = ctk.CTkEntry(ai_tab, height=35, textvariable=self.ai_timeout_var,
                                       font=ctk.CTkFont(size=13))
        ai_timeout_entry.pack(fill="x", padx=20, pady=(0, 20))
    
    def create_buttons(self, parent):
        """Create the bottom buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color=("gray95", "gray15"))
        button_frame.pack(fill="x", pady=(0, 0))
        
        btn_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_container.pack(pady=15, padx=20)
        
        # Save button
        ctk.CTkButton(btn_container, text="💾 Save Settings", command=self.save_and_close,
                     height=40, width=120, font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")
                     ).pack(side="left", padx=(0, 10))
        
        # Apply button
        ctk.CTkButton(btn_container, text="Apply", command=self.apply_settings,
                     height=40, width=80, font=ctk.CTkFont(size=13),
                     fg_color=("blue", "darkblue"), hover_color=("darkblue", "blue")
                     ).pack(side="left", padx=(0, 10))
        
        # Reset button
        ctk.CTkButton(btn_container, text="Reset to Defaults", command=self.reset_settings,
                     height=40, width=120, font=ctk.CTkFont(size=13),
                     fg_color=("orange", "darkorange"), hover_color=("darkorange", "orange")
                     ).pack(side="left", padx=(0, 10))
        
        # Cancel button
        ctk.CTkButton(btn_container, text="Cancel", command=self.close_dialog,
                     height=40, width=80, font=ctk.CTkFont(size=13),
                     fg_color=("gray", "gray40"), hover_color=("darkgray", "gray60")
                     ).pack(side="left")
    
    def test_api_connection(self):
        """Test the API connection"""
        self.test_btn.configure(state="disabled", text="Testing...")
        self.connection_status.configure(text="", text_color=("black", "white"))
        
        def test_connection():
            try:
                url = self.api_url_entry.get().strip()
                if not url:
                    self.connection_status.configure(text="Please enter a URL", text_color="red")
                    return
                
                response = requests.get(f"{url}/projects", timeout=5)
                if response.status_code == 200:
                    self.connection_status.configure(text="✓ Connected successfully", text_color="green")
                else:
                    self.connection_status.configure(text=f"✗ HTTP {response.status_code}", text_color="red")
            except requests.exceptions.ConnectionError:
                self.connection_status.configure(text="✗ Connection failed", text_color="red")
            except requests.exceptions.Timeout:
                self.connection_status.configure(text="✗ Timeout", text_color="red")
            except Exception as e:
                self.connection_status.configure(text=f"✗ Error: {str(e)}", text_color="red")
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
            
            self.settings["appearance"]["theme"] = self.theme_var.get()
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
            else:
                self.show_error_message("Failed to save settings!")
        else:
            self.show_error_message("Invalid settings values!")
    
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
        
        self.theme_var.set(self.settings["appearance"]["theme"])
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
    
    def show_success_message(self, message: str):
        """Show a temporary success message"""
        # Create a temporary label
        if hasattr(self, 'temp_message'):
            self.temp_message.destroy()
        
        self.temp_message = ctk.CTkLabel(self.window, text=message, 
                                        font=ctk.CTkFont(size=12),
                                        text_color="green")
        self.temp_message.pack(pady=5)
        
        # Remove after 3 seconds
        self.window.after(3000, lambda: self.temp_message.destroy() if hasattr(self, 'temp_message') else None)
    
    def show_error_message(self, message: str):
        """Show a temporary error message"""
        # Create a temporary label
        if hasattr(self, 'temp_message'):
            self.temp_message.destroy()
        
        self.temp_message = ctk.CTkLabel(self.window, text=message, 
                                        font=ctk.CTkFont(size=12),
                                        text_color="red")
        self.temp_message.pack(pady=5)
        
        # Remove after 3 seconds
        self.window.after(3000, lambda: self.temp_message.destroy() if hasattr(self, 'temp_message') else None)
    
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
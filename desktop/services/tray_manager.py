"""
Enhanced System Tray Manager for Motivate.AI

Provides a modern system tray interface with quick actions, voice input,
and intelligent notifications.
"""

import pystray
import requests
from PIL import Image, ImageDraw
from threading import Thread
import os
import time
from typing import Optional, Callable


class TrayManager:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.tray_icon = None
        self.running = False
        
        # Create tray icon
        self.create_icon()
        
    def create_icon(self):
        """Create a simple tray icon"""
        # Create a simple icon with a circle and "M" for Motivate
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a blue circle background
        margin = 8
        draw.ellipse([margin, margin, width-margin, height-margin], 
                    fill=(41, 128, 185, 255), outline=(52, 152, 219, 255), width=2)
        
        # Draw "M" in the center (simplified)
        text_bbox = draw.textbbox((0, 0), "M")
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2 - 2
        
        draw.text((text_x, text_y), "M", fill=(255, 255, 255, 255))
        
        return image
    
    def create_menu(self):
        """Create the context menu for the tray icon"""
        menu_items = [
            pystray.MenuItem(
                "🏠 Open Main Window",
                self.show_main_window,
                default=True
            ),
            pystray.MenuItem(
                "➕ Quick Add Task",
                self.quick_add_task
            ),
            pystray.MenuItem(
                "🎤 Voice Add Task",
                self.voice_add_task
            ),
            pystray.MenuItem(
                "⏰ Next Suggestion",
                self.show_next_suggestion
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "📊 Today's Progress",
                self.show_progress
            ),
            pystray.MenuItem(
                "⚙️ Settings",
                self.show_settings
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ Exit",
                self.quit_application
            )
        ]
        
        return pystray.Menu(*menu_items)
    
    def start(self):
        """Start the system tray icon"""
        if self.tray_icon is None:
            icon_image = self.create_icon()
            menu = self.create_menu()
            
            self.tray_icon = pystray.Icon(
                "motivate_ai",
                icon_image,
                "Motivate.AI - AI-Guided Project Companion",
                menu
            )
        
        self.running = True
        # Run tray in a separate thread to avoid blocking
        tray_thread = Thread(target=self._run_tray, daemon=True)
        tray_thread.start()
        
        return tray_thread
    
    def _run_tray(self):
        """Internal method to run the tray icon"""
        try:
            self.tray_icon.run()
        except Exception as e:
            print(f"Tray icon error: {e}")
    
    def stop(self):
        """Stop the system tray icon"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
    
    def update_icon(self, has_notifications=False):
        """Update the tray icon to show notification state"""
        if not self.tray_icon:
            return
            
        # Create icon with notification indicator if needed
        icon_image = self.create_icon()
        
        if has_notifications:
            # Add a small red dot for notifications
            draw = ImageDraw.Draw(icon_image)
            draw.ellipse([45, 10, 55, 20], fill=(231, 76, 60, 255))
        
        self.tray_icon.icon = icon_image
    
    def show_notification(self, title: str, message: str, duration: int = 5):
        """Show a system notification"""
        if self.tray_icon:
            self.tray_icon.notify(message, title)
    
    # Menu action handlers
    def show_main_window(self, icon=None, item=None):
        """Show the main application window"""
        if self.main_window:
            # Bring window to front
            self.main_window.root.deiconify()
            self.main_window.root.lift()
            self.main_window.root.focus_force()
        else:
            # Import and create main window if not provided
            from ui.main_window import MainWindow
            self.main_window = MainWindow()
            self.main_window.run()
    
    def quick_add_task(self, icon=None, item=None):
        """Open quick add task dialog"""
        # For now, show notification - will implement dialog later
        self.show_notification("Quick Add", "Quick add task dialog - Coming soon!")
        
        # TODO: Implement quick add dialog
        # from ui.quick_add import QuickAddDialog
        # dialog = QuickAddDialog()
        # dialog.show()
    
    def voice_add_task(self, icon=None, item=None):
        """Start voice input for adding a task"""
        self.show_notification("Voice Input", "Voice recognition starting...")
        
        # TODO: Implement voice input
        # from services.speech_service import SpeechService
        # speech = SpeechService()
        # speech.start_listening()
    
    def show_next_suggestion(self, icon=None, item=None):
        """Show the next AI suggestion"""
        try:
            # Try to get suggestion from backend
            response = requests.get(f"{self.api_base_url}/suggestions/next", timeout=5)
            if response.status_code == 200:
                suggestion = response.json()
                title = "AI Suggestion"
                message = suggestion.get("text", "No suggestions available")
            else:
                title = "Demo Suggestion"
                message = "Try organizing one drawer in your workshop (5 minutes)"
        except:
            title = "Demo Suggestion"
            message = "Try organizing one drawer in your workshop (5 minutes)"
        
        self.show_notification(title, message)
    
    def show_progress(self, icon=None, item=None):
        """Show today's progress summary"""
        try:
            # Try to get progress from backend
            response = requests.get(f"{self.api_base_url}/progress/today", timeout=5)
            if response.status_code == 200:
                progress = response.json()
                completed = progress.get("completed", 0)
                total = progress.get("total", 0)
                message = f"Today: {completed}/{total} tasks completed"
            else:
                message = "Progress tracking unavailable"
        except:
            message = "Demo: 3/5 tasks completed today ✅"
        
        self.show_notification("Today's Progress", message)
    
    def show_settings(self, icon=None, item=None):
        """Open settings window"""
        self.show_notification("Settings", "Settings window - Coming soon!")
        
        # TODO: Implement settings window
        # from ui.settings import SettingsWindow
        # settings = SettingsWindow()
        # settings.show()
    
    def quit_application(self, icon=None, item=None):
        """Quit the entire application"""
        self.stop()
        
        # Close main window if open
        if self.main_window and hasattr(self.main_window, 'root'):
            try:
                self.main_window.root.quit()
                self.main_window.root.destroy()
            except:
                pass
        
        # Exit the application
        import sys
        sys.exit(0)


# Global tray manager instance
_tray_manager = None

def get_tray_manager(main_window=None) -> TrayManager:
    """Get the global tray manager instance"""
    global _tray_manager
    if _tray_manager is None:
        _tray_manager = TrayManager(main_window)
    return _tray_manager

def start_tray(main_window=None):
    """Start the system tray with optional main window reference"""
    tray = get_tray_manager(main_window)
    return tray.start()

if __name__ == "__main__":
    # Test the tray manager
    tray = TrayManager()
    tray.start()
    
    # Keep the application running
    try:
        while tray.running:
            time.sleep(1)
    except KeyboardInterrupt:
        tray.stop() 
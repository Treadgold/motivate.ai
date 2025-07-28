"""
Fixed System Tray Manager for Motivate.AI
Addresses Python 3.12 + Windows pystray threading issues
Uses queue-based communication for thread safety
"""

import pystray
import requests
from PIL import Image, ImageDraw
import threading
import os
import time
import sys
import queue
from typing import Optional, Callable


class TrayManager:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8010/api/v1")
        self.tray_icon = None
        self.running = False
        self.tray_thread = None
        self.restart_attempts = 0
        self.max_restart_attempts = 3
        
        # Thread-safe communication queue
        self.action_queue = queue.Queue()
        
    def create_icon(self):
        """Create a simple tray icon"""
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a blue circle background
        margin = 8
        draw.ellipse([margin, margin, width-margin, height-margin], 
                    fill=(41, 128, 185, 255), outline=(52, 152, 219, 255), width=2)
        
        # Draw "M" in the center
        try:
            # Try to draw text with better positioning
            font_size = 24
            text_x, text_y = width//2 - 8, height//2 - 15
            draw.text((text_x, text_y), "M", fill=(255, 255, 255, 255))
        except:
            # Fallback if font issues
            text_x, text_y = width//2 - 10, height//2 - 12
            draw.text((text_x, text_y), "M", fill=(255, 255, 255, 255))
        
        return image
    
    def create_menu(self):
        """Create the context menu for the tray icon"""
        menu_items = [
            pystray.MenuItem("🏠 Open Main Window", self.show_main_window, default=True),
            pystray.MenuItem("➕ Quick Add Task", self.quick_add_task),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Settings", self.show_settings),
            pystray.MenuItem("❌ Exit", self.quit_application)
        ]
        return pystray.Menu(*menu_items)
    
    def start(self):
        """Start the system tray icon with auto-restart capability"""
        self.running = True
        self.restart_attempts = 0
        return self._start_tray()
    
    def _start_tray(self):
        """Internal method to start the tray with retry logic"""
        try:
            if self.tray_icon is None:
                icon_image = self.create_icon()
                menu = self.create_menu()
                
                self.tray_icon = pystray.Icon(
                    "motivate_ai",
                    icon_image,
                    "Motivate.AI",
                    menu
                )
            
            # Create a persistent thread that won't exit unexpectedly
            self.tray_thread = threading.Thread(
                target=self._run_tray_persistent, 
                daemon=False,  # Keep as non-daemon
                name="TrayIcon"
            )
            self.tray_thread.start()
            
            return self.tray_thread
            
        except Exception as e:
            print(f"Error starting tray: {e}")
            return None
    
    def _run_tray_persistent(self):
        """Persistent tray runner that keeps the thread alive"""
        while self.running:
            try:
                print("🔄 Starting system tray icon...")
                
                # Create a new icon instance if needed
                if self.tray_icon is None:
                    icon_image = self.create_icon()
                    menu = self.create_menu()
                    self.tray_icon = pystray.Icon(
                        "motivate_ai",
                        icon_image,
                        "Motivate.AI",
                        menu
                    )
                
                # Run the tray icon
                self.tray_icon.run()
                
            except Exception as e:
                print(f"Tray icon error: {e}")
                self.restart_attempts += 1
                
                if self.restart_attempts < self.max_restart_attempts and self.running:
                    print(f"🔄 Restarting tray icon (attempt {self.restart_attempts}/{self.max_restart_attempts})...")
                    time.sleep(2)  # Wait before retry
                    
                    # Reset the tray icon for retry
                    self.tray_icon = None
                    continue
                else:
                    print("❌ Max restart attempts reached, tray will remain stopped")
                    break
            
            # If we get here, the tray stopped normally or we're not running anymore
            if not self.running:
                break
                
        print("🛑 Tray thread exiting")
    
    def stop(self):
        """Stop the system tray icon"""
        print("🔄 Stopping system tray...")
        self.running = False
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception as e:
                print(f"Error stopping tray icon: {e}")
        
        if self.tray_thread and self.tray_thread.is_alive():
            try:
                self.tray_thread.join(timeout=3)
                if self.tray_thread.is_alive():
                    print("⚠️ Tray thread did not stop cleanly")
            except Exception as e:
                print(f"Error joining tray thread: {e}")
    
    def get_pending_actions(self):
        """Get any pending actions from the queue (thread-safe)"""
        actions = []
        while True:
            try:
                action = self.action_queue.get_nowait()
                actions.append(action)
            except queue.Empty:
                break
        return actions
    
    # Menu action handlers - these run in the tray thread
    def show_main_window(self, icon=None, item=None):
        """Queue main window show request for main thread"""
        print("📱 Open Main Window requested")
        try:
            self.action_queue.put(("show_main_window", {}))
        except Exception as e:
            print(f"Error queuing main window action: {e}")
    
    def quick_add_task(self, icon=None, item=None):
        """Queue quick add task request for main thread"""
        print("➕ Quick Add Task requested")
        try:
            self.action_queue.put(("quick_add_task", {}))
        except Exception as e:
            print(f"Error queuing quick add action: {e}")
    
    def show_settings(self, icon=None, item=None):
        """Queue settings request for main thread"""
        print("⚙️ Settings requested")
        try:
            self.action_queue.put(("show_settings", {}))
        except Exception as e:
            print(f"Error queuing settings action: {e}")
    
    def quit_application(self, icon=None, item=None):
        """Queue quit request for main thread"""
        print("🛑 Exit requested")
        try:
            self.action_queue.put(("quit_application", {}))
            self.stop()
        except Exception as e:
            print(f"Error queuing quit action: {e}")


# Global instance
_tray_manager = None

def get_tray_manager() -> TrayManager:
    """Get the global tray manager instance"""
    global _tray_manager
    if _tray_manager is None:
        _tray_manager = TrayManager()
    return _tray_manager

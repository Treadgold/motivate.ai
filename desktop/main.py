"""
Motivate.AI Desktop App - Enhanced Main Application

Integrates the CustomTkinter UI, system tray, popup notifications,
idle monitoring, and speech recognition into a complete desktop experience.
"""

import os
import sys
import time
import threading
import signal
from pathlib import Path

# Add the desktop directory to the Python path
desktop_dir = Path(__file__).parent
sys.path.insert(0, str(desktop_dir))

# Core imports
from dotenv import load_dotenv
import requests

# UI Components
from ui.main_window import MainWindow
from ui.popup_manager import get_popup_manager
from ui.quick_add import show_quick_add

# Services
from services.tray_manager_fixed import get_tray_manager
from services.idle_monitor import get_smart_idle_manager

# Load environment variables
load_dotenv()

class MotivateAIApp:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        self.idle_threshold = int(os.getenv("IDLE_THRESHOLD_MINUTES", "10"))
        
        # Application state
        self.running = False
        self.main_window = None
        self.tray_manager = None
        self.popup_manager = None
        self.idle_manager = None
        
        # Threads
        self.tray_thread = None
        
        print("🚀 Initializing Motivate.AI Desktop App...")
        
    def initialize_components(self):
        """Initialize all application components"""
        
        # Initialize popup manager first (needed by other components)
        self.popup_manager = get_popup_manager()
        print("✅ Pop-up manager initialized")
        
        # Initialize idle monitoring with popup integration (temporarily disabled for stability)
        # self.idle_manager = get_smart_idle_manager(self.popup_manager)
        self.idle_manager = None
        print(f"⚠️ Idle monitoring temporarily disabled for stability")
        
        # PRE-CREATE the main window on main thread (but keep it hidden)
        print("🔄 Creating main window on main thread...")
        self.main_window = MainWindow()
        self.main_window.root.withdraw()  # Hide it initially
        print("✅ Main window pre-created and hidden")
        
        # Initialize tray manager (will create main window when needed)
        self.tray_manager = get_tray_manager()
        print("✅ System tray manager initialized")
        
        # Set up cross-component communication
        self.setup_integrations()
        
    def setup_integrations(self):
        """Set up communication between components"""
        # Queue-based communication is now handled automatically
        # No need to override tray manager methods
        print("✅ Component integrations configured")
    
    def on_task_added(self, task_data):
        """Handle when a new task is added"""
        print(f"📝 New task added: {task_data['title']}")
        
        # Refresh main window if open
        if self.main_window:
            self.main_window.load_tasks_list()
        
        # Show notification
        if self.tray_manager:
            self.tray_manager.show_notification(
                "Task Added", 
                f"Added: {task_data['title']}"
            )
    
    def check_backend_connection(self) -> bool:
        """Test if the backend API is running"""
        try:
            health_url = self.api_base_url.replace('/api/v1', '/health')
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Backend connection failed: {e}")
            return False
    
    def start(self):
        """Start the application"""
        print("\n" + "="*50)
        print("🌟 MOTIVATE.AI DESKTOP APP")
        print("="*50)
        print(f"API URL: {self.api_base_url}")
        print(f"Idle threshold: {self.idle_threshold} minutes")
        print()
        
        # Check backend connection
        if self.check_backend_connection():
            print("✅ Backend connection successful")
        else:
            print("⚠️  Backend not available - running in offline mode")
        
        print()
        
        # Initialize components
        self.initialize_components()
        
        # Start services
        self.start_services()
        
        # Set application as running
        self.running = True
        
        print("🎯 Application started successfully!")
        print("\nRunning services:")
        print("  • System tray with context menu")
        print("  • Pre-created main window (hidden)")
        print("  • Smart pop-up notifications")
        print("  • Voice input support (coming soon)")
        print("\nTray menu options:")
        print("  • 🏠 Open Main Window")
        print("  • ➕ Quick Add Task")
        print("  • 🎤 Voice Add Task")
        print("  • ⏰ Next Suggestion")
        print("  • 📊 Today's Progress")
        print("  • ⚙️ Settings")
        print("  • ❌ Exit")
        print()
        print("💡 Right-click the system tray icon to access features")
        print("🔤 Press Ctrl+C to stop")
        print()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Main application loop
        self.main_loop()
    
    def start_services(self):
        """Start all background services"""
        
        # Start system tray (in background thread)
        self.tray_thread = self.tray_manager.start()
        print("🔄 System tray started")
        
        # Start idle monitoring (temporarily disabled)
        # if self.idle_manager:
        #     self.idle_manager.start()
        #     print("🔄 Idle monitoring started")
        print("⚠️ Idle monitoring disabled for stability")
        
        # Give services time to initialize
        time.sleep(1)
    
    def main_loop(self):
        """Main application event loop"""
        try:
            last_status_time = 0
            status_interval = 300  # Show status every 5 minutes
            
            while self.running:
                current_time = time.time()
                
                # Process any pending tray actions (thread-safe)
                self.process_tray_actions()
                
                # Update main window if it exists
                if self.main_window and self.main_window.root.winfo_exists():
                    try:
                        self.main_window.root.update()
                        # Process any pending updates
                        self.main_window.process_pending_updates()
                    except:
                        pass  # Window might be destroyed
                
                # Show periodic status
                if current_time - last_status_time > status_interval:
                    self.show_status()
                    last_status_time = current_time
                
                # Check if tray thread is still running and try to restart it
                if self.tray_thread and not self.tray_thread.is_alive():
                    print("⚠️  System tray thread stopped, attempting restart...")
                    # Try to restart the tray once
                    try:
                        self.tray_thread = self.tray_manager._start_tray()
                        if self.tray_thread:
                            print("✅ System tray restarted")
                        else:
                            print("❌ Failed to restart tray, continuing without it...")
                            self.tray_thread = None
                    except Exception as e:
                        print(f"❌ Failed to restart tray: {e}")
                        print("🔄 Continuing without system tray...")
                        self.tray_thread = None
                
                time.sleep(0.1)  # Reduced sleep for more responsive action processing
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"\n💥 Unexpected error in main loop: {e}")
        finally:
            self.shutdown()
    
    def process_tray_actions(self):
        """Process pending actions from the tray manager (runs on main thread)"""
        if not self.tray_manager:
            return
            
        actions = self.tray_manager.get_pending_actions()
        for action, params in actions:
            try:
                if action == "show_main_window":
                    self.show_main_window_safe()
                elif action == "quick_add_task":
                    self.quick_add_task_safe()
                elif action == "show_settings":
                    self.show_settings_safe()
                elif action == "quit_application":
                    self.quit_application_safe()
                else:
                    print(f"Unknown action: {action}")
            except Exception as e:
                print(f"Error processing action {action}: {e}")
    
    def show_main_window_safe(self):
        """Safely show main window on main thread"""
        try:
            print("📱 Opening main window...")
            
            if not self.main_window or not self.main_window.root.winfo_exists():
                print("🔄 Main window doesn't exist, creating new one...")
                self.main_window = MainWindow()
                print("✅ Main window created")
            
            # Show window and process any pending updates
            self.main_window.show_window()
            print("✅ Main window opened")
            
        except Exception as e:
            print(f"❌ Error opening main window: {e}")
            import traceback
            traceback.print_exc()
    
    def quick_add_task_safe(self):
        """Safely show quick add dialog on main thread"""
        try:
            print("➕ Opening quick add dialog...")
            show_quick_add(on_task_added=self.on_task_added)
        except Exception as e:
            print(f"❌ Error opening quick add: {e}")
    
    def show_settings_safe(self):
        """Safely show settings dialog on main thread"""
        print("⚙️ Settings - Coming soon!")
        # Future: implement settings dialog
    
    def quit_application_safe(self):
        """Safely quit application on main thread"""
        print("🛑 Quitting application...")
        self.running = False

    def show_status(self):
        """Show current application status"""
        if self.idle_manager:
            status = self.idle_manager.get_status()
            idle_time = status.get('idle_minutes', 0)
            is_idle = status.get('is_idle', False)
            
            status_icon = "😴" if is_idle else "🏃"
            print(f"{status_icon} Status: {time.strftime('%H:%M:%S')} - "
                  f"Idle: {idle_time:.1f}m - "
                  f"Monitoring: {'✅' if status.get('monitoring') else '❌'}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM"
        }
        signal_name = signal_names.get(signum, f"Signal {signum}")
        print(f"\n🛑 Received {signal_name} - initiating shutdown...")
        self.running = False
    
    def shutdown(self):
        """Gracefully shutdown the application"""
        print("\n🔄 Shutting down Motivate.AI...")
        
        self.running = False
        
        # Stop idle monitoring
        if self.idle_manager:
            self.idle_manager.stop()
            print("✅ Idle monitoring stopped")
        
        # Dismiss any active popups
        if self.popup_manager:
            self.popup_manager.dismiss_active_popups()
            print("✅ Pop-ups dismissed")
        
        # Stop system tray
        if self.tray_manager:
            self.tray_manager.stop()
            print("✅ System tray stopped")
        
        # Close main window if open
        if self.main_window and hasattr(self.main_window, 'root'):
            try:
                self.main_window.root.quit()
                self.main_window.root.destroy()
                print("✅ Main window closed")
            except:
                pass
        
        print("👋 Motivate.AI Desktop App stopped successfully")
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        app = MotivateAIApp()
        app.start()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 
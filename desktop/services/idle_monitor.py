"""
Idle Monitoring Service for Motivate.AI

Detects user idle time and triggers appropriate interventions
when the user has been inactive for specified periods.
"""

import time
import threading
from typing import Callable, Optional
import os
import psutil

# Windows-specific imports
try:
    import win32api
    import win32gui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class IdleMonitor:
    def __init__(self, idle_threshold_minutes: int = 10):
        self.idle_threshold_minutes = idle_threshold_minutes
        self.idle_threshold_seconds = idle_threshold_minutes * 60
        self.monitoring = False
        self.monitor_thread = None
        
        # Callbacks
        self.on_idle_detected: Optional[Callable[[int], None]] = None
        self.on_activity_resumed: Optional[Callable[[], None]] = None
        self.on_long_idle: Optional[Callable[[int], None]] = None
        
        # State tracking
        self.last_activity_time = time.time()
        self.was_idle = False
        self.idle_start_time = None
        
        # Check system capabilities
        self.can_monitor = self._check_capabilities()
        
    def _check_capabilities(self) -> bool:
        """Check if we can monitor system idle time"""
        if WINDOWS_AVAILABLE:
            return True
        
        # For non-Windows systems, we can still do basic process monitoring
        return True
    
    def get_system_idle_time(self) -> float:
        """Get system idle time in seconds"""
        if WINDOWS_AVAILABLE:
            return self._get_windows_idle_time()
        else:
            return self._get_fallback_idle_time()
    
    def _get_windows_idle_time(self) -> float:
        """Get idle time using Windows API"""
        try:
            # Get last input info using Windows API
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', wintypes.UINT),
                    ('dwTime', wintypes.DWORD),
                ]
            
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            
            if user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
                current_time = kernel32.GetTickCount()
                idle_time = current_time - lastInputInfo.dwTime
                return idle_time / 1000.0  # Convert to seconds
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error getting Windows idle time: {e}")
            return self._get_fallback_idle_time()
    
    def _get_fallback_idle_time(self) -> float:
        """Fallback method using process activity monitoring"""
        try:
            # Monitor CPU usage and active processes as a proxy for activity
            current_time = time.time()
            
            # Check if there are any high-activity processes
            high_activity_threshold = 5.0  # CPU usage percentage
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    cpu_percent = proc.info['cpu_percent']
                    if cpu_percent and cpu_percent > high_activity_threshold:
                        # Recent activity detected
                        self.last_activity_time = current_time
                        return 0.0
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # No high activity detected
            return current_time - self.last_activity_time
            
        except Exception as e:
            print(f"Error in fallback idle detection: {e}")
            return 0.0
    
    def start_monitoring(self):
        """Start idle time monitoring"""
        if self.monitoring:
            return
            
        if not self.can_monitor:
            print("Warning: Idle monitoring not fully supported on this system")
            return
        
        self.monitoring = True
        # Create thread with more explicit settings for stability
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True,
            name="IdleMonitor"
        )
        self.monitor_thread.start()
        print(f"Idle monitoring started (threshold: {self.idle_threshold_minutes} minutes)")
    
    def stop_monitoring(self):
        """Stop idle time monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=2)
                if self.monitor_thread.is_alive():
                    print("Warning: Monitor thread did not stop cleanly")
            except Exception as e:
                print(f"Error stopping monitor thread: {e}")
        print("Idle monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop - thread-safe version"""
        check_interval = 30  # Check every 30 seconds
        long_idle_threshold = self.idle_threshold_seconds * 3  # 3x the normal threshold
        
        while self.monitoring:
            try:
                current_idle_time = self.get_system_idle_time()
                idle_minutes = current_idle_time / 60
                
                # Check for initial idle state
                if not self.was_idle and current_idle_time >= self.idle_threshold_seconds:
                    self.was_idle = True
                    self.idle_start_time = time.time() - current_idle_time
                    
                    print(f"Idle detected: {idle_minutes:.1f} minutes")
                    
                    # Use thread-safe callback execution
                    if self.on_idle_detected:
                        try:
                            self.on_idle_detected(int(idle_minutes))
                        except Exception as callback_error:
                            print(f"Error in idle callback: {callback_error}")
                
                # Check for long idle periods
                elif self.was_idle and current_idle_time >= long_idle_threshold:
                    if self.on_long_idle:
                        try:
                            self.on_long_idle(int(idle_minutes))
                        except Exception as callback_error:
                            print(f"Error in long idle callback: {callback_error}")
                
                # Check for activity resumption
                elif self.was_idle and current_idle_time < self.idle_threshold_seconds:
                    self.was_idle = False
                    self.idle_start_time = None
                    
                    print("Activity resumed")
                    
                    if self.on_activity_resumed:
                        try:
                            self.on_activity_resumed()
                        except Exception as callback_error:
                            print(f"Error in activity resumed callback: {callback_error}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in idle monitoring loop: {e}")
                # Continue monitoring even if there's an error
                try:
                    time.sleep(check_interval)
                except:
                    break  # Exit if we can't even sleep
    
    def get_current_idle_time(self) -> float:
        """Get current idle time in minutes"""
        return self.get_system_idle_time() / 60
    
    def is_currently_idle(self) -> bool:
        """Check if user is currently idle"""
        return self.get_system_idle_time() >= self.idle_threshold_seconds
    
    def set_threshold(self, minutes: int):
        """Set new idle threshold"""
        self.idle_threshold_minutes = minutes
        self.idle_threshold_seconds = minutes * 60
        print(f"Idle threshold set to {minutes} minutes")
    
    def get_idle_status(self) -> dict:
        """Get current idle status information"""
        current_idle = self.get_system_idle_time()
        
        return {
            "is_idle": current_idle >= self.idle_threshold_seconds,
            "idle_seconds": current_idle,
            "idle_minutes": current_idle / 60,
            "threshold_minutes": self.idle_threshold_minutes,
            "monitoring": self.monitoring
        }


class SmartIdleManager:
    """Enhanced idle manager with smart intervention logic"""
    
    def __init__(self, popup_manager=None):
        self.idle_monitor = IdleMonitor()
        self.popup_manager = popup_manager
        self.intervention_history = []
        
        # Smart intervention settings
        self.settings = {
            "gentle_threshold_minutes": 10,    # First gentle nudge
            "suggestion_threshold_minutes": 20, # Task suggestions
            "break_threshold_minutes": 60,     # Break reminders
            "max_interventions_per_hour": 3
        }
        
        # Set up callbacks
        self.idle_monitor.on_idle_detected = self.handle_idle_detected
        self.idle_monitor.on_activity_resumed = self.handle_activity_resumed
        self.idle_monitor.on_long_idle = self.handle_long_idle
    
    def start(self):
        """Start smart idle monitoring"""
        self.idle_monitor.start_monitoring()
    
    def stop(self):
        """Stop idle monitoring"""
        self.idle_monitor.stop_monitoring()
    
    def handle_idle_detected(self, idle_minutes: int):
        """Handle when idle state is first detected"""
        print(f"Smart idle manager: User idle for {idle_minutes} minutes")
        
        if self.should_intervene():
            if idle_minutes >= self.settings["gentle_threshold_minutes"]:
                self.trigger_gentle_intervention(idle_minutes)
    
    def handle_activity_resumed(self):
        """Handle when user becomes active again"""
        print("Smart idle manager: User activity resumed")
        
        # Could trigger a "welcome back" or progress check
        if self.popup_manager:
            # Check if user completed anything during the break
            pass
    
    def handle_long_idle(self, idle_minutes: int):
        """Handle extended idle periods"""
        print(f"Smart idle manager: Extended idle period - {idle_minutes} minutes")
        
        if idle_minutes >= self.settings["break_threshold_minutes"]:
            self.suggest_break_activities()
        elif idle_minutes >= self.settings["suggestion_threshold_minutes"]:
            self.trigger_task_suggestion(idle_minutes)
    
    def should_intervene(self) -> bool:
        """Check if we should intervene based on history and settings"""
        from datetime import datetime, timedelta
        
        # Check intervention frequency
        recent_interventions = [
            i for i in self.intervention_history
            if (datetime.now() - i["timestamp"]) < timedelta(hours=1)
        ]
        
        return len(recent_interventions) < self.settings["max_interventions_per_hour"]
    
    def trigger_gentle_intervention(self, idle_minutes: int):
        """Trigger a gentle nudge intervention"""
        if self.popup_manager:
            self.popup_manager.show_gentle_nudge(idle_minutes)
            self.log_intervention("gentle_nudge", {"idle_minutes": idle_minutes})
    
    def trigger_task_suggestion(self, idle_minutes: int):
        """Trigger a specific task suggestion"""
        # This could integrate with the backend to get contextual suggestions
        if self.popup_manager:
            # For now, use the gentle nudge - could be enhanced to specific tasks
            self.popup_manager.show_gentle_nudge(idle_minutes)
            self.log_intervention("task_suggestion", {"idle_minutes": idle_minutes})
    
    def suggest_break_activities(self):
        """Suggest break activities for very long idle periods"""
        if self.popup_manager:
            # Could suggest break activities like walking, stretching, etc.
            pass
    
    def log_intervention(self, intervention_type: str, data: dict):
        """Log intervention for learning and frequency control"""
        from datetime import datetime
        
        self.intervention_history.append({
            "timestamp": datetime.now(),
            "type": intervention_type,
            "data": data
        })
        
        # Keep only last 50 interventions
        if len(self.intervention_history) > 50:
            self.intervention_history = self.intervention_history[-50:]
    
    def get_status(self) -> dict:
        """Get current idle monitoring status"""
        idle_status = self.idle_monitor.get_idle_status()
        
        return {
            **idle_status,
            "smart_monitoring": True,
            "recent_interventions": len([
                i for i in self.intervention_history
                if (time.time() - i["timestamp"].timestamp()) < 3600
            ]),
            "settings": self.settings
        }


# Global instances
_idle_monitor = None
_smart_idle_manager = None

def get_idle_monitor() -> IdleMonitor:
    """Get the global idle monitor instance"""
    global _idle_monitor
    if _idle_monitor is None:
        _idle_monitor = IdleMonitor()
    return _idle_monitor

def get_smart_idle_manager(popup_manager=None) -> SmartIdleManager:
    """Get the global smart idle manager instance"""
    global _smart_idle_manager
    if _smart_idle_manager is None:
        _smart_idle_manager = SmartIdleManager(popup_manager)
    return _smart_idle_manager

if __name__ == "__main__":
    # Test the idle monitor
    monitor = IdleMonitor(idle_threshold_minutes=1)  # 1 minute for testing
    
    def on_idle(minutes):
        print(f"CALLBACK: User idle for {minutes} minutes")
    
    def on_active():
        print("CALLBACK: User is active again")
    
    monitor.on_idle_detected = on_idle
    monitor.on_activity_resumed = on_active
    
    monitor.start_monitoring()
    
    try:
        while True:
            status = monitor.get_idle_status()
            print(f"Current idle: {status['idle_minutes']:.1f} minutes")
            time.sleep(10)
    except KeyboardInterrupt:
        monitor.stop_monitoring() 
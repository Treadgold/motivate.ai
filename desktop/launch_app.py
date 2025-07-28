"""
Motivate.AI Desktop App Launcher

Simple launcher that opens the main task management window directly.
This avoids threading conflicts and provides reliable access to the app.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    print("🚀 Starting Motivate.AI Desktop App...")
    
    try:
        # Import and run the main window directly
        from ui.main_window import MainWindow
        
        print("✅ Creating main window...")
        app = MainWindow()
        
        print("✅ Starting application...")
        print("\n🎯 Motivate.AI is now running!")
        print("📋 Manage your tasks and projects in the window that just opened")
        print("🔤 Press Ctrl+C here to stop the app")
        print()
        
        # Run the main window
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Motivate.AI stopping...")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")

if __name__ == "__main__":
    main() 
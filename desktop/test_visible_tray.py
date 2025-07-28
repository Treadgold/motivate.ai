"""
Test script that shows a notification to help locate the system tray icon
"""

import time
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🎯 SYSTEM TRAY ICON LOCATOR TEST")
print("=" * 40)

try:
    from services.tray_manager import TrayManager
    
    print("Creating tray with notification...")
    tray = TrayManager()
    tray.start()
    
    # Give it a moment to start
    time.sleep(2)
    
    print("\n🔔 SHOWING NOTIFICATION NOW!")
    print("   This will help you locate the icon...")
    
    # Show a notification that will help locate the icon
    tray.show_notification(
        "🎉 Motivate.AI is Running!", 
        "Click this notification or look for the blue M icon in your system tray"
    )
    
    print("\n👀 LOOK FOR:")
    print("   • A Windows notification popup (just appeared)")
    print("   • A blue circle with white 'M' in system tray")
    print("   • Check the hidden icons area (click ^ arrow)")
    print("\n⏰ Keeping icon visible for 30 seconds...")
    
    for i in range(30, 0, -1):
        if i % 5 == 0:  # Show reminder every 5 seconds
            print(f"   🔍 Still looking... {i} seconds left")
        time.sleep(1)
    
    print("\n🛑 Stopping test...")
    tray.stop()
    print("   ✅ Test complete - icon should now be gone")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n📍 NEXT STEPS:")
print(f"   1. If you saw the notification: The app is working!")
print(f"   2. If you found the icon: Right-click it for the menu")
print(f"   3. If still no icon: Check Windows notification settings")
print(f"   4. The main app should still be running in background") 
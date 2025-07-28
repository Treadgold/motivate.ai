"""
Simple test script to verify system tray functionality
"""

import time
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("Testing system tray functionality...")

try:
    print("1. Importing TrayManager...")
    from services.tray_manager import TrayManager
    print("   ✅ TrayManager imported successfully")
    
    print("2. Creating TrayManager instance...")
    tray = TrayManager()
    print("   ✅ TrayManager created")
    
    print("3. Starting system tray...")
    tray.start()
    print("   ✅ Tray started")
    print("\n🔍 CHECK YOUR SYSTEM TRAY NOW!")
    print("   Look for a blue circle with 'M' icon")
    print("   Right-click it to see the menu")
    print("\n⏰ Waiting 15 seconds for you to test...")
    
    for i in range(15, 0, -1):
        print(f"   {i} seconds remaining...", end='\r')
        time.sleep(1)
    
    print("\n4. Stopping tray...")
    tray.stop()
    print("   ✅ Test complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest finished.") 
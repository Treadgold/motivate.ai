"""
Motivate.AI Desktop App - System Tray Application
Basic implementation for Windows idle detection and notifications
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
IDLE_THRESHOLD = int(os.getenv("IDLE_THRESHOLD_MINUTES", "10"))

def check_backend_connection():
    """Test if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Motivate.AI Desktop App Starting...")
    print(f"API URL: {API_BASE_URL}")
    print(f"Idle threshold: {IDLE_THRESHOLD} minutes")
    print()
    
    # Check backend connection
    if check_backend_connection():
        print("✅ Backend connection successful")
    else:
        print("❌ Cannot connect to backend")
        print("Make sure the backend is running:")
        print("  cd backend && venv\\Scripts\\activate && python main.py")
        print()
        input("Press Enter to continue anyway (for testing)...")
    
    print()
    print("Desktop app is running...")
    print("(This is a basic version - full features coming soon)")
    print()
    print("Features planned:")
    print("- System tray icon")
    print("- Idle time detection") 
    print("- Smart notifications")
    print("- Project suggestions")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        # Simple loop - in the real version this would be replaced with
        # actual idle monitoring and tray functionality
        while True:
            time.sleep(60)
            print(f"Desktop app running... {time.strftime('%H:%M:%S')}")
            
    except KeyboardInterrupt:
        print("\n👋 Desktop app stopping...")
        sys.exit(0)

if __name__ == "__main__":
    main() 
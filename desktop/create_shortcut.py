"""
Create Desktop Shortcut for Motivate.AI

This script creates a desktop shortcut so you can easily access the app.
"""

import os
import winshell
from win32com.client import Dispatch
from pathlib import Path

def create_shortcut():
    """Create a desktop shortcut for Motivate.AI"""
    
    # Get paths
    desktop_dir = Path.home() / "Desktop"
    current_dir = Path(__file__).parent.absolute()
    batch_file = current_dir / "start_desktop.bat"
    
    # Shortcut details
    shortcut_name = "Motivate.AI Desktop App.lnk"
    shortcut_path = desktop_dir / shortcut_name
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(batch_file)
    shortcut.WorkingDirectory = str(current_dir)
    shortcut.IconLocation = str(batch_file)
    shortcut.Description = "Motivate.AI - AI-Guided Project Companion"
    shortcut.save()
    
    print(f"✅ Desktop shortcut created: {shortcut_path}")
    print("🎯 You can now double-click the shortcut to open Motivate.AI!")
    
    # Also suggest pinning to taskbar
    print(f"\n📌 To pin to taskbar:")
    print(f"   1. Right-click the desktop shortcut")
    print(f"   2. Select 'Pin to taskbar'")

if __name__ == "__main__":
    try:
        create_shortcut()
    except ImportError:
        print("❌ winshell not available. Creating simple instructions instead...")
        print(f"\n📋 Manual shortcut creation:")
        print(f"   1. Right-click on your desktop")
        print(f"   2. Select 'New' → 'Shortcut'")
        print(f"   3. Browse to: {Path(__file__).parent.absolute() / 'start_desktop.bat'}")
        print(f"   4. Name it: 'Motivate.AI Desktop App'")
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        print(f"\n📁 You can manually run: {Path(__file__).parent.absolute() / 'start_desktop.bat'}") 
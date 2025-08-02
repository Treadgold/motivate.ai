#!/usr/bin/env python3
"""
Test script for the settings dialog
"""

import customtkinter as ctk
import sys
import os

# Add the current directory to the path so we can import ui modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.settings_dialog import show_settings_dialog

def main():
    # Set up the application
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window (hidden)
    app = ctk.CTk()
    app.withdraw()  # Hide the main window
    
    def on_settings_saved(settings):
        """Callback when settings are saved"""
        print("Settings saved successfully!")
        print(f"API URL: {settings['api']['base_url']}")
        print(f"Theme: {settings['appearance']['theme']}")
        print(f"Color theme: {settings['appearance']['color_theme']}")
    
    # Show the settings dialog
    print("Opening settings dialog...")
    show_settings_dialog(app, on_settings_saved)
    
    # Start the main loop
    app.mainloop()

if __name__ == "__main__":
    main() 
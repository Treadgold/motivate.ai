"""
AI Button Tooltip Helper

Provides hover tooltips for AI buttons to improve user understanding.
"""

import customtkinter as ctk
import tkinter as tk

class ToolTip:
    """
    Create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tooltip_window = None

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Arial", 10, "normal"))
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def add_ai_button_tooltip(button, task_data):
    """Add informative tooltip to AI button"""
    estimated_time = task_data.get("estimated_time", 0)
    title_length = len(task_data.get("title", ""))
    
    if estimated_time > 15 or title_length > 25:
        tooltip_text = (f"🤖 AI Task Splitting\n\n"
                       f"Break this task into smaller, manageable pieces\n"
                       f"• Estimated time: {estimated_time} min\n"
                       f"• Title complexity: {'High' if title_length > 40 else 'Medium'}\n\n"
                       f"Click to analyze with AI (takes 10-30 seconds)")
    else:
        tooltip_text = (f"🤖 AI Assistant\n\n"
                       f"This task is already quite manageable,\n"
                       f"but AI can still help break it down further\n\n"
                       f"Click to analyze with AI (takes 10-30 seconds)")
    
    ToolTip(button, tooltip_text) 
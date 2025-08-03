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
    estimated_time = task_data.get("estimated_minutes", 0)
    title_length = len(task_data.get("title", ""))
    description = task_data.get("description", "")
    
    # Determine if task could benefit from splitting or description improvement
    needs_splitting = estimated_time > 15 or title_length > 25
    needs_description = not description or len(description.strip()) < 20
    
    if needs_splitting and needs_description:
        tooltip_text = (f"🤖 AI Task Assistant\n\n"
                       f"Multiple AI capabilities available:\n"
                       f"• Split Task - Break into smaller pieces\n"
                       f"• Improve Description - Add more detail\n\n"
                       f"Estimated time: {estimated_time} min\n"
                       f"Description: {'Missing/Brief' if needs_description else 'Complete'}\n\n"
                       f"Click to choose AI capability (takes 10-30 seconds)")
    elif needs_splitting:
        tooltip_text = (f"🤖 AI Task Assistant\n\n"
                       f"Recommended: Split this complex task\n"
                       f"• Split Task - Break into manageable pieces\n"
                       f"• Improve Description - Enhance details\n\n"
                       f"Estimated time: {estimated_time} min\n\n"
                       f"Click to choose AI capability (takes 10-30 seconds)")
    elif needs_description:
        tooltip_text = (f"🤖 AI Task Assistant\n\n"
                       f"Recommended: Improve task description\n"
                       f"• Split Task - Break into subtasks\n"
                       f"• Improve Description - Add actionable details\n\n"
                       f"Description: {'Missing' if not description else 'Brief'}\n\n"
                       f"Click to choose AI capability (takes 10-30 seconds)")
    else:
        tooltip_text = (f"🤖 AI Task Assistant\n\n"
                       f"AI capabilities available:\n"
                       f"• Split Task - Break into smaller pieces\n"
                       f"• Improve Description - Enhance clarity\n\n"
                       f"This task looks well-structured, but AI can\n"
                       f"still help optimize it further\n\n"
                       f"Click to choose AI capability (takes 10-30 seconds)")
    
    ToolTip(button, tooltip_text) 
"""
AI Assistant Dialog

Beautiful dialog for showing AI task assistance including task splitting,
description improvement, and other AI capabilities with reasoning,
confidence scores, and user approval/rejection options.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Any, Callable, Optional
import threading
import time

class AIAssistantDialog:
    def __init__(self, parent, task_data: Dict, on_approve: Callable, on_cancel: Callable, default_operation: str = "split_task"):
        """
        Initialize the AI assistant dialog
        
        Args:
            parent: Parent window
            task_data: Original task data
            on_approve: Callback when user approves (preview_data)
            on_cancel: Callback when user cancels
            default_operation: Default operation to select ("split_task" or "improve_description")
        """
        self.parent = parent
        self.task_data = task_data
        self.on_approve = on_approve
        self.on_cancel = on_cancel
        self.preview_data = None
        self.current_operation = default_operation
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("🤖 AI Task Assistant")
        self.dialog.geometry("900x750")
        self.dialog.resizable(True, True)
        self.dialog.minsize(800, 650)
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.center_dialog()
        
        # Configure grid weights
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(2, weight=1)  # Updated for operation selection row
        
        # Setup UI
        self.setup_ui()
        
        # Don't start analysis immediately - wait for user to select operation or click analyze
        # self.start_ai_analysis()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 900
        dialog_height = 750
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Header
        self.create_header()
        
        # Operation selection area
        self.create_operation_selection()
        
        # Main content area (scrollable)
        self.main_frame = ctk.CTkScrollableFrame(self.dialog)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Footer with action buttons
        self.create_footer()
        
        # Initially show selection state
        self.show_selection_state()
    
    def create_header(self):
        """Create the dialog header"""
        header_frame = ctk.CTkFrame(self.dialog, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # AI icon and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        ai_icon = ctk.CTkLabel(title_frame, text="🤖", font=ctk.CTkFont(size=32))
        ai_icon.grid(row=0, column=0, padx=(0, 15))
        
        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.grid(row=0, column=1)
        
        title_label = ctk.CTkLabel(title_text, text="AI Task Assistant", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(title_text, text="Choose an AI capability to enhance your task", 
                                     font=ctk.CTkFont(size=12), text_color="gray")
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Close button
        close_btn = ctk.CTkButton(header_frame, text="✕", width=40, height=40,
                                 command=self.close_dialog,
                                 fg_color="transparent", 
                                 hover_color=("gray70", "gray30"))
        close_btn.grid(row=0, column=1, sticky="e", padx=20, pady=20)
    
    def create_operation_selection(self):
        """Create the operation selection area"""
        selection_frame = ctk.CTkFrame(self.dialog, height=100)
        selection_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 0))
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # Operation selection label
        operation_label = ctk.CTkLabel(selection_frame, text="🎯 Select AI Capability:", 
                                      font=ctk.CTkFont(size=14, weight="bold"))
        operation_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        # Operation dropdown
        operation_options = [
            "Split Task - Break down into manageable subtasks",
            "Improve Description - Enhance task details and clarity"
        ]
        
        # Map display names to operation values
        self.operation_map = {
            "Split Task - Break down into manageable subtasks": "split_task",
            "Improve Description - Enhance task details and clarity": "improve_description"
        }
        
        # Set default selection based on current operation
        default_display = next((k for k, v in self.operation_map.items() if v == self.current_operation), 
                              operation_options[0])
        
        self.operation_dropdown = ctk.CTkOptionMenu(selection_frame, 
                                                   values=operation_options,
                                                   command=self.on_operation_changed,
                                                   width=500,
                                                   font=ctk.CTkFont(size=12))
        self.operation_dropdown.set(default_display)
        self.operation_dropdown.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Analyze button
        self.analyze_btn = ctk.CTkButton(selection_frame, text="🔍 Analyze Task", 
                                        command=self.start_ai_analysis,
                                        width=150, height=40,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        fg_color=("blue", "darkblue"), 
                                        hover_color=("darkblue", "blue"))
        self.analyze_btn.grid(row=1, column=1, sticky="e", padx=20, pady=(0, 10))
    
    def on_operation_changed(self, selected_option: str):
        """Handle operation selection change"""
        self.current_operation = self.operation_map[selected_option]
        # Reset preview data when operation changes
        self.preview_data = None
        # Show selection state again
        self.show_selection_state()
    
    def create_footer(self):
        """Create the dialog footer with action buttons"""
        self.footer_frame = ctk.CTkFrame(self.dialog, height=80)
        self.footer_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        self.status_icon = ctk.CTkLabel(self.status_frame, text="🔄", font=ctk.CTkFont(size=16))
        self.status_icon.grid(row=0, column=0, padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Analyzing task...", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.grid(row=0, column=1)
        
        # Action buttons
        self.action_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.action_frame.grid(row=0, column=1, sticky="e", padx=20, pady=20)
        
        # Cancel button (always available)
        self.cancel_btn = ctk.CTkButton(self.action_frame, text="✕ Cancel", width=100, height=40,
                                       command=self.close_dialog,
                                       fg_color=("gray", "gray40"), 
                                       hover_color=("gray60", "gray20"))
        self.cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Approve button (hidden initially)
        self.approve_btn = ctk.CTkButton(self.action_frame, text="✓ Apply Changes", width=120, height=40,
                                        command=self.approve_changes,
                                        fg_color=("green", "darkgreen"), 
                                        hover_color=("darkgreen", "green"))
        # Will be shown when preview is ready
    
    def show_selection_state(self):
        """Show initial selection state"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Update status
        self.status_icon.configure(text="🎯")
        self.status_label.configure(text="Select an AI capability and click Analyze Task")
        
        # Hide approve button
        self.approve_btn.grid_remove()
        
        # Selection instructions
        instruction_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        instruction_frame.grid(row=0, column=0, pady=50)
        
        # Instruction icon
        instruction_icon = ctk.CTkLabel(instruction_frame, text="👆", font=ctk.CTkFont(size=48))
        instruction_icon.grid(row=0, column=0, pady=(0, 20))
        
        instruction_text = ctk.CTkLabel(instruction_frame, text="Choose your AI capability above and click 'Analyze Task' to get started", 
                                       font=ctk.CTkFont(size=16, weight="bold"))
        instruction_text.grid(row=1, column=0, pady=(0, 10))
        
        instruction_detail = ctk.CTkLabel(instruction_frame, 
                                         text="• Split Task: Break complex tasks into manageable subtasks\n• Improve Description: Enhance task details for better clarity",
                                         font=ctk.CTkFont(size=12), text_color="gray",
                                         justify="left")
        instruction_detail.grid(row=2, column=0)
    
    def show_loading_state(self):
        """Show loading animation while AI analyzes"""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Loading animation
        loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        loading_frame.grid(row=0, column=0, pady=100)
        
        # Animated AI icon
        self.loading_icon = ctk.CTkLabel(loading_frame, text="🤖", font=ctk.CTkFont(size=64))
        self.loading_icon.grid(row=0, column=0, pady=(0, 20))
        
        # Dynamic loading text based on operation
        if self.current_operation == "split_task":
            loading_text_str = "AI is analyzing your task for splitting..."
            loading_subtitle_str = "⏰ This typically takes 10-30 seconds\n🧠 Breaking down complexity and identifying optimal subtasks\n💡 Please be patient while AI works its magic"
        else:  # improve_description
            loading_text_str = "AI is improving your task description..."
            loading_subtitle_str = "⏰ This typically takes 10-30 seconds\n🧠 Analyzing context and enhancing details\n💡 Please be patient while AI crafts better description"
        
        loading_text = ctk.CTkLabel(loading_frame, text=loading_text_str, 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        loading_text.grid(row=1, column=0, pady=(0, 10))
        
        loading_subtitle = ctk.CTkLabel(loading_frame, 
                                       text=loading_subtitle_str,
                                       font=ctk.CTkFont(size=12), text_color="gray",
                                       justify="center")
        loading_subtitle.grid(row=2, column=0)
        
        # Add progress indicator
        progress_text = ctk.CTkLabel(loading_frame, 
                                    text="🔄 Processing...", 
                                    font=ctk.CTkFont(size=11), text_color="blue")
        progress_text.grid(row=3, column=0, pady=(15, 0))
        
        # Start loading animation
        self.animate_loading()
    
    def animate_loading(self):
        """Animate the loading icon"""
        if hasattr(self, 'loading_icon') and self.loading_icon.winfo_exists():
            current_text = self.loading_icon.cget("text")
            if current_text == "🤖":
                self.loading_icon.configure(text="🧠")
            elif current_text == "🧠":
                self.loading_icon.configure(text="💭")
            else:
                self.loading_icon.configure(text="🤖")
            
            # Continue animation every 500ms
            self.dialog.after(500, self.animate_loading)
    
    def start_ai_analysis(self):
        """Start AI analysis in background thread with polling-based result handling"""
        # Show loading state immediately for instant user feedback
        self.show_loading_state()
        
        # Initialize result storage
        self.analysis_result = None
        self.analysis_error = None
        self.analysis_complete = False
        
        def analyze_task():
            try:
                # Import here to avoid circular imports
                import requests
                import os
                
                api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
                
                # Make request to AI agent based on current operation
                if self.current_operation == "split_task":
                    request_data = {
                        "operation": "split_task",
                        "task_ids": [self.task_data.get("id")],
                        "context": {
                            "user_preference": "prefer smaller, manageable tasks",
                            "work_style": "focused work sessions"
                        }
                    }
                else:  # improve_description
                    request_data = {
                        "operation": "improve_description",
                        "task_ids": [self.task_data.get("id")],
                        "context": {
                            "user_preference": "detailed, actionable descriptions",
                            "goal": "make tasks easier to understand and execute"
                        }
                    }
                
                response = requests.post(f"{api_base_url}/ai-agent/preview", 
                                       json=request_data, timeout=600)
                
                if response.status_code == 200:
                    preview_data = response.json()
                    print(f"DEBUG: Received preview data with keys: {list(preview_data.keys())}")
                    self.analysis_result = preview_data
                else:
                    error_msg = f"API Error: {response.status_code}"
                    if response.text:
                        try:
                            error_detail = response.json().get("detail", response.text)
                            error_msg = f"Error: {error_detail}"
                        except:
                            error_msg = f"Error: {response.text[:100]}"
                    self.analysis_error = error_msg
                    
            except requests.exceptions.Timeout:
                self.analysis_error = "⏰ AI analysis timed out\n\nThis usually happens when:\n• The AI model is starting up\n• The backend is processing another request\n• Network connectivity issues\n\nPlease try again in a moment."
            except requests.exceptions.ConnectionError:
                self.analysis_error = "🔌 Cannot connect to AI service\n\nPlease check:\n• Backend server is running (python backend/main.py)\n• Server is accessible at http://127.0.0.1:8010\n• No firewall blocking the connection"
            except Exception as e:
                self.analysis_error = f"💥 Unexpected error occurred\n\nDetails: {str(e)}\n\nPlease try again or check the console for more information."
            finally:
                self.analysis_complete = True
        
        # Start background analysis
        thread = threading.Thread(target=analyze_task, daemon=True)
        thread.start()
        
        # Start polling for results
        self.check_analysis_result()
    
    def check_analysis_result(self):
        """Poll for analysis results and update UI when complete"""
        try:
            if not hasattr(self, 'dialog') or not self.dialog.winfo_exists():
                print("Dialog was closed before analysis completed")
                return
                
            if self.analysis_complete:
                if self.analysis_result:
                    print("DEBUG: Analysis completed successfully, showing preview")
                    self.show_preview(self.analysis_result)
                elif self.analysis_error:
                    print(f"DEBUG: Analysis failed with error: {self.analysis_error[:100]}...")
                    self.show_error(self.analysis_error)
                else:
                    print("DEBUG: Analysis completed but no result or error found")
                    self.show_error("Analysis completed but no results were returned")
            else:
                # Continue polling every 100ms
                self.dialog.after(100, self.check_analysis_result)
        except Exception as e:
            print(f"ERROR: Exception in check_analysis_result: {e}")
            try:
                self.show_error(f"Failed to process analysis results: {str(e)}")
            except:
                print("Could not show error - dialog may have been destroyed")
    
    def show_preview(self, preview_data: Dict):
        """Show the AI analysis preview"""
        try:
            print(f"DEBUG: show_preview called with confidence: {preview_data.get('confidence_score', 'N/A')}")
            self.preview_data = preview_data
            
            # Update status
            confidence = preview_data.get("confidence_score", 0.0)
            self.status_icon.configure(text="✨")
            if self.current_operation == "split_task":
                self.status_label.configure(text=f"Task analysis complete! Confidence: {confidence:.0%}")
                self.approve_btn.configure(text="✓ Split Task")
            else:  # improve_description
                self.status_label.configure(text=f"Description analysis complete! Confidence: {confidence:.0%}")
                self.approve_btn.configure(text="✓ Update Description")
            
            # Show approve button
            self.approve_btn.grid(row=0, column=1, padx=(0, 0))
            
            # Clear main frame
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            # Create preview content
            self.create_preview_content(preview_data)
            print("DEBUG: Preview displayed successfully")
        except Exception as e:
            print(f"ERROR: Exception in show_preview: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Failed to display preview: {str(e)}")
    
    def create_preview_content(self, preview_data: Dict):
        """Create the preview content showing AI analysis"""
        # Original task section
        self.create_original_task_section()
        
        # AI reasoning section
        self.create_reasoning_section(preview_data)
        
        if self.current_operation == "split_task":
            # Proposed subtasks section
            self.create_subtasks_section(preview_data)
        else:  # improve_description
            # Improved description section
            self.create_improved_description_section(preview_data)
        
        # Confidence and impact section
        self.create_confidence_section(preview_data)
    
    def create_original_task_section(self):
        """Create section showing the original task"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(section_frame, text="📋 Original Task", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Task details
        task_details_frame = ctk.CTkFrame(section_frame, fg_color=("gray95", "gray10"))
        task_details_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        task_details_frame.grid_columnconfigure(0, weight=1)
        
        # Task title
        title_label = ctk.CTkLabel(task_details_frame, text=self.task_data.get("title", "Untitled Task"),
                                  font=ctk.CTkFont(size=14, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Task description
        description = self.task_data.get("description", "No description")
        if description and description.strip():
            desc_label = ctk.CTkLabel(task_details_frame, text=description,
                                     font=ctk.CTkFont(size=12), 
                                     wraplength=800, justify="left")
            desc_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        
        # Task metadata
        metadata_text = []
        estimated_minutes = self.task_data.get("estimated_minutes") or self.task_data.get("estimated_time")
        if estimated_minutes:
            metadata_text.append(f"⏱️ {estimated_minutes} minutes")
        if self.task_data.get("priority"):
            metadata_text.append(f"📌 {self.task_data.get('priority').title()} priority")
        
        if metadata_text:
            meta_label = ctk.CTkLabel(task_details_frame, text=" • ".join(metadata_text),
                                     font=ctk.CTkFont(size=11), text_color="gray")
            meta_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))
    
    def create_reasoning_section(self, preview_data: Dict):
        """Create section showing AI reasoning"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(section_frame, text="🧠 AI Analysis & Reasoning", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
         
         # Reasoning content
        reasoning_frame = ctk.CTkFrame(section_frame, fg_color=("#E3F2FD", "#1976D2"))
        reasoning_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        reasoning_frame.grid_columnconfigure(0, weight=1)
        
        reasoning_text = preview_data.get("reasoning", "AI analysis completed")
        reasoning_label = ctk.CTkLabel(reasoning_frame, text=reasoning_text,
                                      font=ctk.CTkFont(size=12), 
                                      wraplength=800, justify="left")
        reasoning_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
    
    def create_subtasks_section(self, preview_data: Dict):
        """Create section showing proposed subtasks"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        proposed_changes = preview_data.get("proposed_changes", [])
        create_action = next((change for change in proposed_changes if change.get("action") == "create_tasks"), None)
        subtask_count = len(create_action.get("tasks", [])) if create_action else 0
        
        header_label = ctk.CTkLabel(section_frame, text=f"✨ Proposed Subtasks ({subtask_count})", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        if create_action and create_action.get("tasks"):
            # Show subtasks
            for i, subtask in enumerate(create_action.get("tasks", [])):
                self.create_subtask_card(section_frame, subtask, i + 1)
        else:
            # No subtasks proposed
            no_tasks_label = ctk.CTkLabel(section_frame, text="No subtasks were proposed by the AI",
                                         font=ctk.CTkFont(size=12), text_color="gray")
            no_tasks_label.grid(row=1, column=0, pady=20)
    
    def create_subtask_card(self, parent, subtask: Dict, index: int):
        """Create a card for each proposed subtask"""
        card_frame = ctk.CTkFrame(parent, fg_color=("gray95", "gray15"))
        card_frame.grid(row=index, column=0, sticky="ew", padx=20, pady=(0, 10))
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Task number badge
        badge_frame = ctk.CTkFrame(card_frame, width=40, height=40, corner_radius=20,
                                  fg_color=("blue", "darkblue"))
        badge_frame.grid(row=0, column=0, padx=15, pady=15, sticky="n")
        
        badge_label = ctk.CTkLabel(badge_frame, text=str(index), 
                                  font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        badge_label.grid(row=0, column=0, padx=8, pady=8)
        
        # Task content
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=15)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Task title
        title_label = ctk.CTkLabel(content_frame, text=subtask.get("title", "Untitled Subtask"),
                                  font=ctk.CTkFont(size=13, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Task description
        description = subtask.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(content_frame, text=description,
                                     font=ctk.CTkFont(size=11), 
                                     wraplength=600, justify="left", text_color="gray")
            desc_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
        
        # Task metadata
        metadata_parts = []
        if subtask.get("estimated_minutes"):
            metadata_parts.append(f"⏱️ {subtask.get('estimated_minutes')} min")
        if subtask.get("priority"):
            metadata_parts.append(f"📌 {subtask.get('priority').title()}")
        if subtask.get("context"):
            metadata_parts.append(f"💡 {subtask.get('context')}")
        
        if metadata_parts:
            meta_label = ctk.CTkLabel(content_frame, text=" • ".join(metadata_parts),
                                     font=ctk.CTkFont(size=10), text_color="gray")
            meta_label.grid(row=2, column=0, sticky="w")
    
    def create_improved_description_section(self, preview_data: Dict):
        """Create section showing the improved description"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(section_frame, text="✨ Improved Description", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Get the improved description from proposed changes
        proposed_changes = preview_data.get("proposed_changes", [])
        update_action = next((change for change in proposed_changes if change.get("action") == "update_task"), None)
        
        if update_action and update_action.get("updates"):
            new_description = update_action["updates"].get("description", "No improved description found")
            
            # Before/After comparison
            comparison_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            comparison_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
            comparison_frame.grid_columnconfigure(0, weight=1)
            comparison_frame.grid_columnconfigure(1, weight=1)
            
            # Original description (left side)
            original_frame = ctk.CTkFrame(comparison_frame, fg_color=("gray95", "gray15"))
            original_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
            original_frame.grid_columnconfigure(0, weight=1)
            
            original_title = ctk.CTkLabel(original_frame, text="📝 Current Description", 
                                         font=ctk.CTkFont(size=13, weight="bold"))
            original_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
            
            original_desc = self.task_data.get("description", "No description")
            if not original_desc or original_desc.strip() == "":
                original_desc = "(No description provided)"
                
            original_text = ctk.CTkLabel(original_frame, text=original_desc,
                                        font=ctk.CTkFont(size=11), 
                                        wraplength=350, justify="left",
                                        text_color="gray")
            original_text.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
            
            # Improved description (right side)  
            improved_frame = ctk.CTkFrame(comparison_frame, fg_color=("#E8F5E8", "#2E7D32"))
            improved_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
            improved_frame.grid_columnconfigure(0, weight=1)
            
            improved_title = ctk.CTkLabel(improved_frame, text="✨ Improved Description", 
                                         font=ctk.CTkFont(size=13, weight="bold"))
            improved_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
            
            improved_text = ctk.CTkLabel(improved_frame, text=new_description,
                                        font=ctk.CTkFont(size=11), 
                                        wraplength=350, justify="left")
            improved_text.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
            
            # Improvements summary
            improvements_frame = ctk.CTkFrame(section_frame, fg_color=("#E3F2FD", "#1976D2"))
            improvements_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 15))
            improvements_frame.grid_columnconfigure(0, weight=1)
            
            improvements_title = ctk.CTkLabel(improvements_frame, text="🎯 Key Improvements", 
                                             font=ctk.CTkFont(size=12, weight="bold"))
            improvements_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
            
            # Extract improvements from reasoning or create summary
            reasoning = preview_data.get("reasoning", "")
            if "improvements:" in reasoning.lower():
                improvements_text = reasoning.split("improvements:", 1)[1].strip()
            else:
                improvements_text = "• Added more specific details and context\n• Clarified expected outcomes and success criteria\n• Improved actionability and clarity"
                
            improvements_label = ctk.CTkLabel(improvements_frame, text=improvements_text,
                                             font=ctk.CTkFont(size=11), 
                                             wraplength=800, justify="left")
            improvements_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        else:
            # No improvements found
            no_improvements_label = ctk.CTkLabel(section_frame, text="No description improvements were proposed by the AI",
                                               font=ctk.CTkFont(size=12), text_color="gray")
            no_improvements_label.grid(row=1, column=0, pady=20)
    
    def create_confidence_section(self, preview_data: Dict):
        """Create section showing confidence and impact assessment"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(section_frame, text="📊 Confidence & Impact Assessment", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Confidence and impact grid
        metrics_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        
        # Confidence score
        confidence = preview_data.get("confidence_score", 0.0)
        conf_frame = ctk.CTkFrame(metrics_frame, fg_color=("#E8F5E8", "#2E7D32"))
        conf_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        
        conf_title = ctk.CTkLabel(conf_frame, text="🎯 Confidence Score", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        conf_title.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        conf_value = ctk.CTkLabel(conf_frame, text=f"{confidence:.0%}", 
                                 font=ctk.CTkFont(size=24, weight="bold"), text_color="green")
        conf_value.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        # Impact assessment
        impact = preview_data.get("estimated_impact", "Moderate impact expected")
        impact_frame = ctk.CTkFrame(metrics_frame, fg_color=("orange", "darkorange"))
        impact_frame.grid(row=0, column=1, sticky="ew", padx=(10, 50), pady=5)
        
        impact_title = ctk.CTkLabel(impact_frame, text="📈 Expected Impact", 
                                   font=ctk.CTkFont(size=14, weight="bold"))
        impact_title.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        impact_text = ctk.CTkLabel(impact_frame, text=impact,
                                  font=ctk.CTkFont(size=11), 
                                  wraplength=300, justify="center")
        impact_text.grid(row=1, column=0, padx=15, pady=(0, 15))
    
    def show_error(self, error_message: str):
        """Show error state"""
        # Update status
        self.status_icon.configure(text="❌")
        self.status_label.configure(text="Analysis failed")
        
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Error display
        error_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        error_frame.grid(row=0, column=0, pady=100)
        
        error_icon = ctk.CTkLabel(error_frame, text="❌", font=ctk.CTkFont(size=64))
        error_icon.grid(row=0, column=0, pady=(0, 20))
        
        error_title = ctk.CTkLabel(error_frame, text="AI Analysis Failed", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        error_title.grid(row=1, column=0, pady=(0, 10))
        
        error_detail = ctk.CTkLabel(error_frame, text=error_message,
                                   font=ctk.CTkFont(size=12), text_color="gray",
                                   wraplength=600, justify="center")
        error_detail.grid(row=2, column=0)
        
        # Action buttons frame
        button_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        
        # Try again button
        retry_btn = ctk.CTkButton(button_frame, text="🔄 Try Again", 
                                 command=self.retry_analysis,
                                 fg_color=("blue", "darkblue"))
        retry_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Close button
        close_btn = ctk.CTkButton(button_frame, text="❌ Close", 
                                 command=self.close_dialog,
                                 fg_color=("gray", "gray40"))
        close_btn.grid(row=0, column=1, padx=(10, 0))
    
    def retry_analysis(self):
        """Retry the AI analysis"""
        self.show_loading_state()
        self.start_ai_analysis()
    
    def approve_changes(self):
        """User approved the changes - execute them"""
        if self.preview_data:
            self.on_approve(self.preview_data)
        self.close_dialog()
    
    def close_dialog(self):
        """Close the dialog"""
        if self.preview_data is None:
            # User cancelled before seeing results
            self.on_cancel()
        self.dialog.destroy()


def show_ai_assistant_dialog(parent, task_data: Dict, on_approve: Callable, on_cancel: Callable = None, default_operation: str = "split_task"):
    """
    Show the AI assistant dialog with multiple capabilities
    
    Args:
        parent: Parent window
        task_data: Task data to process
        on_approve: Callback when approved (preview_data)
        on_cancel: Callback when cancelled (optional)
        default_operation: Default operation to select ("split_task" or "improve_description")
    """
    if on_cancel is None:
        on_cancel = lambda: None
    
    dialog = AIAssistantDialog(parent, task_data, on_approve, on_cancel, default_operation)
    return dialog

def show_ai_split_dialog(parent, task_data: Dict, on_approve: Callable, on_cancel: Callable = None):
    """
    Show the AI split task dialog (backward compatibility)
    
    Args:
        parent: Parent window
        task_data: Task data to split
        on_approve: Callback when approved (preview_data)
        on_cancel: Callback when cancelled (optional)
    """
    return show_ai_assistant_dialog(parent, task_data, on_approve, on_cancel, "split_task")

def show_ai_improve_description_dialog(parent, task_data: Dict, on_approve: Callable, on_cancel: Callable = None):
    """
    Show the AI improve description dialog
    
    Args:
        parent: Parent window
        task_data: Task data to improve description for
        on_approve: Callback when approved (preview_data)
        on_cancel: Callback when cancelled (optional)
    """
    return show_ai_assistant_dialog(parent, task_data, on_approve, on_cancel, "improve_description") 
"""
Main entry point for the Motivate.AI Mobile Application

This module serves as the entry point when the motivate_ai package 
is executed as a module (python -m motivate_ai).
"""

from .app import MotivateAIApp


def main():
    """Main entry point for the application"""
    app = MotivateAIApp()
    return app


if __name__ == "__main__":
    app = main()
    app.main_loop()
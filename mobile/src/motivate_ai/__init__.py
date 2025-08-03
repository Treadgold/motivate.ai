"""
Motivate.AI Mobile - Cross-Platform Task and Project Management

A BeeWare application for managing projects and tasks with AI assistance.
Built with Toga for native cross-platform performance.
"""

__version__ = "0.1.0"
__author__ = "Motivate.AI Team"
__email__ = "team@motivate.ai"

# Package metadata
PACKAGE_NAME = "motivate_ai"
DISPLAY_NAME = "Motivate.AI"
DESCRIPTION = "Task and project management with AI assistance"

# API Configuration
DEFAULT_API_URL = "http://192.168.56.1:8010/api/v1"
API_TIMEOUT = 30

# App Configuration
STORAGE_VERSION = 1
MAX_OFFLINE_TASKS = 1000
SYNC_INTERVAL = 300  # 5 minutes
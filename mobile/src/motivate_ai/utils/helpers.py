"""
Helper utilities for Motivate.AI Mobile Application

This module contains common utility functions used throughout the application
for formatting, validation, and other helper operations.
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse


def format_datetime(dt: datetime, format_type: str = "relative") -> str:
    """Format datetime for display
    
    Args:
        dt: Datetime to format
        format_type: Format type ("relative", "short", "long")
        
    Returns:
        Formatted datetime string
    """
    now = datetime.now()
    
    if format_type == "relative":
        return _format_relative_time(dt, now)
    elif format_type == "short":
        return dt.strftime("%m/%d %H:%M")
    elif format_type == "long":
        return dt.strftime("%B %d, %Y at %H:%M")
    else:
        return dt.isoformat()


def _format_relative_time(dt: datetime, now: datetime) -> str:
    """Format datetime as relative time (e.g., '2 hours ago')"""
    if dt.tzinfo is None and now.tzinfo is None:
        # Both are naive, safe to compare
        pass
    elif dt.tzinfo is not None and now.tzinfo is not None:
        # Both are timezone-aware, safe to compare
        pass
    else:
        # Mix of naive and aware - make both naive for comparison
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
    
    diff = now - dt
    
    if diff.total_seconds() < 0:
        # Future time
        diff = abs(diff)
        suffix = "from now"
    else:
        suffix = "ago"
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return f"{seconds} seconds {suffix}" if seconds != 1 else f"1 second {suffix}"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes {suffix}" if minutes != 1 else f"1 minute {suffix}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours {suffix}" if hours != 1 else f"1 hour {suffix}"
    elif seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} days {suffix}" if days != 1 else f"1 day {suffix}"
    else:
        # For longer periods, use absolute format
        return dt.strftime("%B %d, %Y")


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string (e.g., "1h 30m", "45m")
    """
    if minutes < 1:
        return "0m"
    elif minutes < 60:
        return f"{minutes}m"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"


def validate_url(url: str) -> bool:
    """Validate if string is a valid URL
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    return text[:truncated_length].rstrip() + suffix


def clean_description(description: Optional[str]) -> str:
    """Clean and format task/project description
    
    Args:
        description: Raw description text
        
    Returns:
        Cleaned description
    """
    if not description:
        return ""
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', description.strip())
    
    # Convert basic markdown elements for display
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove bold markers
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)      # Remove italic markers
    
    return cleaned


def safe_int(value, default: int = 0) -> int:
    """Safely convert value to integer
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_completion_percentage(completed: int, total: int) -> float:
    """Calculate completion percentage
    
    Args:
        completed: Number of completed items
        total: Total number of items
        
    Returns:
        Completion percentage (0.0 to 100.0)
    """
    if total == 0:
        return 0.0
    
    percentage = (completed / total) * 100
    return round(percentage, 1)


def get_priority_color(priority: str) -> str:
    """Get color code for priority level
    
    Args:
        priority: Priority level (low, normal, high, urgent)
        
    Returns:
        Hex color code
    """
    colors = {
        "low": "#4CAF50",      # Green
        "normal": "#2196F3",   # Blue  
        "high": "#FF9800",     # Orange
        "urgent": "#F44336",   # Red
    }
    return colors.get(priority.lower(), colors["normal"])


def get_status_color(status: str) -> str:
    """Get color code for task status
    
    Args:
        status: Task status (pending, in_progress, completed, cancelled)
        
    Returns:
        Hex color code
    """
    colors = {
        "pending": "#9E9E9E",     # Gray
        "in_progress": "#2196F3", # Blue
        "completed": "#4CAF50",   # Green
        "cancelled": "#F44336",   # Red
    }
    return colors.get(status.lower(), colors["pending"])
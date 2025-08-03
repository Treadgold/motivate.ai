"""
Theme Manager for Motivate.AI Desktop

Provides centralized color theme management for consistent light and dark mode support.
All colors are defined here to ensure consistency and easy theme switching.
"""

import customtkinter as ctk
from typing import Dict, Tuple, Optional
from enum import Enum


class ThemeMode(Enum):
    """Available theme modes"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ColorTheme:
    """Centralized color theme management"""
    
    def __init__(self, mode: ThemeMode = ThemeMode.SYSTEM):
        self.mode = mode
        self._current_theme = self._get_effective_theme()
        self._colors = self._get_color_scheme()
    
    def _get_effective_theme(self) -> str:
        """Get the effective theme (light/dark) based on mode and system preference"""
        if self.mode == ThemeMode.SYSTEM:
            # Use CustomTkinter's system detection
            return ctk.get_appearance_mode()
        return self.mode.value
    
    def _get_color_scheme(self) -> Dict[str, str]:
        """Get the color scheme for the current theme"""
        if self._current_theme == "dark":
            return self._dark_colors()
        else:
            return self._light_colors()
    
    def _light_colors(self) -> Dict[str, str]:
        """Light theme color definitions"""
        return {
            # Core Background Colors
            "bg_primary": "#ffffff",           # Main window background
            "bg_secondary": "#f8f9fa",         # Secondary background
            "bg_tertiary": "#e9ecef",          # Tertiary background
            "bg_surface": "#ffffff",           # Surface elements (cards, panels)
            "bg_overlay": "#ffffff",           # Overlay/modal backgrounds
            
            # Surface Colors (Compatible with CustomTkinter fg_color tuples)
            "surface_primary": ("gray90", "gray10"),      # Header frames
            "surface_secondary": ("gray95", "gray15"),    # Button frames
            "surface_elevated": "#ffffff",                # Elevated surface
            "surface_input": "#ffffff",                   # Input field background
            "surface_transparent": "transparent",         # Transparent frames
            
            # Primary Colors (Blue variants)
            "primary_main": "#3b82f6",          # Main primary color
            "primary_hover": "#2563eb",         # Primary hover
            "primary_light": "#eff6ff",         # Primary light variant
            "primary_dark": "#1d4ed8",          # Primary dark variant
            
            # Secondary Colors (Green variants)
            "secondary_main": "#22c55e",        # Main secondary color
            "secondary_hover": "#16a34a",       # Secondary hover
            "secondary_light": "#f0fdf4",       # Secondary light variant
            "secondary_dark": "#15803d",        # Secondary dark variant
            
            # Semantic Colors
            "success_main": "#22c55e",
            "success_hover": "#16a34a",
            "success_light": "#dcfce7",
            "warning_main": "#f59e0b",
            "warning_hover": "#d97706",
            "warning_light": "#fef3c7",
            "error_main": "#ef4444",
            "error_hover": "#dc2626",
            "error_light": "#fee2e2",
            "info_main": "#3b82f6",
            "info_hover": "#2563eb",
            "info_light": "#dbeafe",
            
            # Text Colors
            "text_primary": "#111827",         # Primary text
            "text_secondary": "#6b7280",       # Secondary text
            "text_tertiary": "#9ca3af",        # Tertiary text
            "text_disabled": "#d1d5db",        # Disabled text
            "text_inverse": "#ffffff",         # Text on dark backgrounds
            "text_success": "#16a34a",         # Success text
            "text_warning": "#d97706",         # Warning text
            "text_error": "#dc2626",           # Error text
            "text_info": "#2563eb",            # Info text
            "text_muted": "gray60",            # Muted text (for completed tasks)
            
            # Border Colors
            "border_light": "#e5e7eb",         # Light borders
            "border_medium": "#d1d5db",        # Medium borders
            "border_dark": "#9ca3af",          # Dark borders
            "border_focus": "#3b82f6",         # Focus border
            "border_error": "#ef4444",         # Error border
            "border_default": ("gray60", "gray50"),  # Default border tuple
            
            # Button Colors (tuples for CustomTkinter compatibility)
            "button_primary": ("blue", "darkblue"),
            "button_secondary": ("gray", "gray40"),
            "button_success": ("green", "darkgreen"),
            "button_danger": ("red", "darkred"),
            "button_warning": ("orange", "darkorange"),
            
            # AI-specific Colors
            "ai_primary": ("#1f538d", "#14375e"),
            "ai_background": "#eff6ff",
            "ai_surface": "#dbeafe",
            "ai_reasoning": ("#E3F2FD", "#1976D2"),
            "ai_confidence": ("#E8F5E8", "#2E7D32"),
            
            # Task-specific Colors
            "task_card_normal": ("gray90", "gray13"),
            "task_card_hover": ("gray70", "gray30"),
            "task_card_selected": "#eff6ff",
            
            # Progress and Card Colors
            "progress_bg": "#e5e7eb",
            "card_normal": ("gray90", "gray13"),
            "card_hover": ("gray80", "gray25"),
            
            # Simplified color aliases for easier use
            "primary": "#3b82f6",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "danger_hover": "#dc2626",
        }
    
    def _dark_colors(self) -> Dict[str, str]:
        """Dark theme color definitions"""
        return {
            # Core Background Colors
            "bg_primary": "#0f172a",           # Main window background
            "bg_secondary": "#1e293b",         # Secondary background
            "bg_tertiary": "#334155",          # Tertiary background
            "bg_surface": "#1e293b",           # Surface elements (cards, panels)
            "bg_overlay": "#0f172a",           # Overlay/modal backgrounds
            
            # Surface Colors (Compatible with CustomTkinter fg_color tuples)
            "surface_primary": ("gray20", "gray80"),      # Header frames
            "surface_secondary": ("gray25", "gray75"),    # Button frames
            "surface_elevated": "#475569",                # Elevated surface
            "surface_input": "#334155",                   # Input field background
            "surface_transparent": "transparent",         # Transparent frames
            
            # Primary Colors (Blue variants) - adjusted for dark mode
            "primary_main": "#38bdf8",          # Main primary color
            "primary_hover": "#0ea5e9",         # Primary hover
            "primary_light": "#0c4a6e",         # Primary light variant
            "primary_dark": "#075985",          # Primary dark variant
            
            # Secondary Colors (Green variants) - adjusted for dark mode
            "secondary_main": "#4ade80",        # Main secondary color
            "secondary_hover": "#22c55e",       # Secondary hover
            "secondary_light": "#052e16",       # Secondary light variant
            "secondary_dark": "#166534",        # Secondary dark variant
            
            # Semantic Colors
            "success_main": "#4ade80",
            "success_hover": "#22c55e",
            "success_light": "#052e16",
            "warning_main": "#fbbf24",
            "warning_hover": "#f59e0b",
            "warning_light": "#451a03",
            "error_main": "#f87171",
            "error_hover": "#ef4444",
            "error_light": "#450a0a",
            "info_main": "#38bdf8",
            "info_hover": "#0ea5e9",
            "info_light": "#0c4a6e",
            
            # Text Colors
            "text_primary": "#f8fafc",         # Primary text
            "text_secondary": "#cbd5e1",       # Secondary text
            "text_tertiary": "#94a3b8",        # Tertiary text
            "text_disabled": "#64748b",        # Disabled text
            "text_inverse": "#0f172a",         # Text on light backgrounds
            "text_success": "#4ade80",         # Success text
            "text_warning": "#fbbf24",         # Warning text
            "text_error": "#f87171",           # Error text
            "text_info": "#38bdf8",            # Info text
            "text_muted": "gray40",            # Muted text (for completed tasks)
            
            # Border Colors
            "border_light": "#475569",         # Light borders
            "border_medium": "#64748b",        # Medium borders
            "border_dark": "#94a3b8",          # Dark borders
            "border_focus": "#38bdf8",         # Focus border
            "border_error": "#f87171",         # Error border
            "border_default": ("gray40", "gray60"),  # Default border tuple
            
            # Button Colors (tuples for CustomTkinter compatibility)
            "button_primary": ("blue", "lightblue"),
            "button_secondary": ("gray50", "gray20"),
            "button_success": ("green", "lightgreen"),
            "button_danger": ("red", "lightcoral"),
            "button_warning": ("orange", "lightyellow"),
            
            # AI-specific Colors
            "ai_primary": ("#38bdf8", "#0ea5e9"),
            "ai_background": "#0c4a6e",
            "ai_surface": "#075985",
            "ai_reasoning": ("#1e3a8a", "#3b82f6"),
            "ai_confidence": ("#166534", "#22c55e"),
            
            # Task-specific Colors
            "task_card_normal": ("gray30", "gray70"),
            "task_card_hover": ("gray40", "gray60"),
            "task_card_selected": "#0c4a6e",
            
            # Progress and Card Colors
            "progress_bg": "#475569",
            "card_normal": ("gray30", "gray70"),
            "card_hover": ("gray40", "gray60"),
            
            # Simplified color aliases for easier use
            "primary": "#38bdf8",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "danger": "#f87171",
            "danger_hover": "#ef4444",
        }
    
    def get_color(self, color_key: str) -> str:
        """Get a color by key"""
        return self._colors.get(color_key, "#000000")
    
    def get_colors(self, *color_keys: str) -> Tuple[str, ...]:
        """Get multiple colors by keys"""
        return tuple(self.get_color(key) for key in color_keys)
    
    def get_fg_color(self, color_key: str):
        """Get foreground color (for CustomTkinter compatibility)"""
        color = self.get_color(color_key)
        # Return the color as-is (can be tuple or string)
        return color
    
    def get_text_color(self, color_key: str) -> str:
        """Get text color"""
        return self.get_color(color_key)
    
    def get_border_color(self, color_key: str):
        """Get border color"""
        return self.get_color(color_key)
    
    def get_button_colors(self, button_type: str = "primary") -> Dict[str, str]:
        """Get button colors for a specific button type"""
        base_key = f"button_{button_type}"
        fg_color = self.get_color(base_key)
        
        # Handle tuple colors for hover
        if isinstance(fg_color, tuple):
            hover_color = (fg_color[1], fg_color[0])  # Swap tuple for hover
        else:
            hover_color = self.get_color(f"{button_type}_hover")
        
        return {
            "fg_color": fg_color,
            "hover_color": hover_color,
            "text_color": self.get_color("text_inverse"),
        }
    
    def update_theme(self, mode: ThemeMode):
        """Update the theme mode and refresh colors"""
        self.mode = mode
        self._current_theme = self._get_effective_theme()
        self._colors = self._get_color_scheme()
    
    def get_current_theme(self) -> str:
        """Get the current effective theme"""
        return self._current_theme
    
    def is_dark_mode(self) -> bool:
        """Check if currently in dark mode"""
        return self._current_theme == "dark"
    
    def is_light_mode(self) -> bool:
        """Check if currently in light mode"""
        return self._current_theme == "light"


# Global theme instance
_theme_manager: Optional[ColorTheme] = None


def get_theme_manager() -> ColorTheme:
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ColorTheme()
    return _theme_manager


def set_theme_mode(mode: ThemeMode):
    """Set the theme mode globally"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ColorTheme(mode)
    else:
        _theme_manager.update_theme(mode)
    
    # Update CustomTkinter appearance mode
    if mode == ThemeMode.SYSTEM:
        ctk.set_appearance_mode("system")
    else:
        ctk.set_appearance_mode(mode.value)


def get_color(color_key: str) -> str:
    """Get a color by key from the global theme manager"""
    return get_theme_manager().get_color(color_key)


def get_colors(*color_keys: str) -> Tuple[str, ...]:
    """Get multiple colors by keys from the global theme manager"""
    return get_theme_manager().get_colors(*color_keys)


def get_button_colors(button_type: str = "primary") -> Dict[str, str]:
    """Get button colors for a specific button type"""
    return get_theme_manager().get_button_colors(button_type)


def is_dark_mode() -> bool:
    """Check if currently in dark mode"""
    return get_theme_manager().is_dark_mode()


def is_light_mode() -> bool:
    """Check if currently in light mode"""
    return get_theme_manager().is_light_mode()


# Theme change callback system
_theme_change_callbacks = []


def register_theme_change_callback(callback):
    """Register a callback to be called when theme changes"""
    _theme_change_callbacks.append(callback)


def unregister_theme_change_callback(callback):
    """Unregister a theme change callback"""
    if callback in _theme_change_callbacks:
        _theme_change_callbacks.remove(callback)


def _notify_theme_change():
    """Notify all registered callbacks of theme change"""
    for callback in _theme_change_callbacks:
        try:
            callback()
        except Exception as e:
            print(f"Error in theme change callback: {e}")


def apply_theme_change(mode: ThemeMode):
    """Apply theme change and notify all callbacks"""
    set_theme_mode(mode)
    _notify_theme_change()


# Convenience functions for common color patterns
def get_surface_colors() -> Dict[str, str]:
    """Get surface-related colors"""
    theme = get_theme_manager()
    return {
        "bg": theme.get_color("bg_primary"),
        "surface": theme.get_color("surface_primary"),
        "surface_secondary": theme.get_color("surface_secondary"),
        "surface_elevated": theme.get_color("surface_elevated"),
    }


def get_text_colors() -> Dict[str, str]:
    """Get text-related colors"""
    theme = get_theme_manager()
    return {
        "primary": theme.get_color("text_primary"),
        "secondary": theme.get_color("text_secondary"),
        "tertiary": theme.get_color("text_tertiary"),
        "disabled": theme.get_color("text_disabled"),
        "inverse": theme.get_color("text_inverse"),
    }


if __name__ == "__main__":
    # Test the theme manager
    theme = ColorTheme(ThemeMode.LIGHT)
    print("Light theme colors:")
    print(f"Primary: {theme.get_color('primary_main')}")
    print(f"Text primary: {theme.get_color('text_primary')}")
    print(f"Background: {theme.get_color('bg_primary')}")
    
    theme.update_theme(ThemeMode.DARK)
    print("\nDark theme colors:")
    print(f"Primary: {theme.get_color('primary_main')}")
    print(f"Text primary: {theme.get_color('text_primary')}")
    print(f"Background: {theme.get_color('bg_primary')}")
# Settings Guide - Motivate.AI Desktop

## Overview

The Settings dialog provides comprehensive configuration options for the Motivate.AI desktop application. You can access it by clicking the ⚙️ (settings) icon in the top-right toolbar of the main window.

## Accessing Settings

1. Open the Motivate.AI desktop application
2. Look for the ⚙️ (gear) icon in the top-right corner of the toolbar
3. Click the settings icon to open the settings dialog

## Settings Categories

### 1. API Settings
Configure connection to the backend API:
- **API Base URL**: The URL of your Motivate.AI backend server (default: `http://127.0.0.1:8010/api/v1`)
- **Request Timeout**: How long to wait for API responses (default: 10 seconds)
- **Auto-connect on startup**: Automatically connect to the API when the app starts
- **Test Connection**: Button to verify the API connection is working

### 2. Appearance Settings
Customize the visual appearance of the application:
- **Theme**: Choose between Light, Dark, or System (follows your OS theme)
- **Color Theme**: Select from Blue, Green, or Dark Blue color schemes
- **Font Size**: Choose Small, Normal, or Large text size
- **Sidebar Width**: Set the width of the projects sidebar in pixels
- **Task Detail Width**: Set the width of the task detail pane in pixels

### 3. Notification Settings
Configure notification preferences:
- **Enable notifications**: Turn all notifications on/off
- **Task reminders**: Receive reminders for upcoming tasks
- **AI status alerts**: Get notified about AI service status changes
- **Enable sound notifications**: Play sounds for notifications

### 4. Behavior Settings
Configure application behavior:
- **Auto-save changes**: Automatically save changes without prompting
- **Confirm deletions**: Ask for confirmation before deleting items
- **Show tooltips**: Display helpful tooltips on hover
- **Start minimized to system tray**: Launch the app minimized to the system tray

### 5. AI Settings
Configure AI assistant behavior:
- **Auto-check AI status**: Automatically check AI service status
- **Show AI suggestions**: Display AI-powered suggestions
- **AI Request Timeout**: How long to wait for AI responses (default: 30 seconds)

## Saving and Applying Settings

### Save Settings
- Click **💾 Save Settings** to save all changes and close the dialog
- Click **Apply** to save changes without closing the dialog

### Reset to Defaults
- Click **Reset to Defaults** to restore all settings to their original values

### Cancel Changes
- Click **Cancel** to close the dialog without saving changes

## Settings Storage

Settings are automatically saved to:
- **Windows**: `%USERPROFILE%\.motivate_ai\settings.json`
- **macOS/Linux**: `~/.motivate_ai/settings.json`

The settings file is created automatically when you first save settings.

## Troubleshooting

### API Connection Issues
1. Verify your backend server is running
2. Check the API Base URL is correct
3. Use the "Test Connection" button to verify connectivity
4. Ensure your firewall allows the connection

### Settings Not Applied
1. Try clicking "Apply" instead of just "Save Settings"
2. Restart the application to ensure all settings take effect
3. Check the console for any error messages

### Reset All Settings
If you encounter issues, you can:
1. Close the application
2. Delete the settings file: `~/.motivate_ai/settings.json`
3. Restart the application (it will use default settings)

## Keyboard Shortcuts

- **Enter**: Save settings and close dialog
- **Escape**: Cancel and close dialog
- **Ctrl+S**: Apply settings (when dialog is focused)

## Tips

- **Test API Connection**: Always test your API connection after changing the URL
- **Theme Changes**: Theme changes are applied immediately
- **Layout Changes**: Sidebar and task detail width changes take effect after restart
- **Backup Settings**: You can copy the settings.json file to backup your configuration 
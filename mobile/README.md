# Mobile App - BeeWare Cross-Platform Application

A BeeWare/Toga mobile app for managing projects and receiving motivation prompts on the go. Built with Python, runs natively on Android, iOS, and more.

## 🚀 Setup

1. Install Python 3.8+ and pip
2. Install BeeWare: `pip install briefcase`
3. Navigate to mobile directory: `cd mobile`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize BeeWare project (if not already done): `briefcase new`

## 🏃 Running

### Development Mode
```bash
briefcase dev
```

### Android Development
```bash
briefcase run android
```

### Build APK
```bash
briefcase package android
```

### iOS Development (macOS only)
```bash
briefcase run iOS
```

## ✨ Features

- **Project Management**: View and edit projects with native UI
- **Task Management**: Track tasks and mark completed
- **Cross-Platform**: Runs on Android, iOS, Windows, macOS, Linux
- **Native Performance**: Pure Python with native widgets
- **Offline Support**: Basic functionality without internet
- **AI Integration**: Smart task splitting and suggestions

## 📁 Structure

```
mobile/
├── src/
│   └── motivate_ai/
│       ├── __init__.py         # Package initialization
│       ├── app.py             # Main application entry point
│       ├── models/            # Data models
│       │   ├── __init__.py
│       │   ├── project.py     # Project data model
│       │   └── task.py        # Task data model
│       ├── services/          # API and business logic
│       │   ├── __init__.py
│       │   ├── api_client.py  # Backend API client
│       │   └── storage.py     # Local data storage
│       ├── ui/                # User interface screens
│       │   ├── __init__.py
│       │   ├── main_window.py # Main application window
│       │   ├── project_list.py # Projects screen
│       │   ├── task_list.py   # Tasks screen
│       │   └── task_form.py   # Task creation/editing
│       └── utils/             # Helper functions
│           ├── __init__.py
│           └── helpers.py     # Utility functions
├── pyproject.toml             # Project configuration & dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

Update `src/motivate_ai/services/api_client.py`:
```python
API_BASE_URL = 'http://your-backend-url:8010/api/v1'
```

For local development, use your computer's IP address instead of localhost.

## 🛠️ Development Commands

```bash
# Run in development mode
briefcase dev

# Create new platforms
briefcase create android
briefcase create iOS

# Run on specific platform
briefcase run android
briefcase run iOS

# Package for distribution
briefcase package android --adhoc  # For testing
briefcase package android          # For release

# Update dependencies
briefcase update
```

## 📱 Platform Support

- **Android**: Native APK builds
- **iOS**: Native iOS builds (requires macOS and Xcode)
- **Windows**: Native Windows executable
- **macOS**: Native macOS application
- **Linux**: Native Linux application
- **Web**: Progressive Web App (future) 
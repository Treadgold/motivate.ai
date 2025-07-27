# Desktop App - Windows Tray Application

A Windows system tray application that monitors user activity and provides gentle motivation prompts.

## 🚀 Setup

```bash
cd desktop
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 🏃 Running

```bash
python main.py
```

The app will start in the system tray (look for the icon in the bottom-right corner).

## ✨ Features

- **Idle Detection**: Monitors mouse/keyboard activity
- **Smart Notifications**: Suggests 15-minute tasks when you're idle
- **Tray Interface**: Right-click for quick actions
- **Background Sync**: Connects to the backend API

## 📁 Structure

```
desktop/
├── main.py              # Application entry point
├── tray_app.py          # System tray functionality
├── idle_monitor.py      # Idle time detection
├── notifications.py     # Windows notifications
├── api_client.py        # Backend API communication
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

Create a `.env` file:
```
API_BASE_URL=http://localhost:8000/api/v1
IDLE_THRESHOLD_MINUTES=10
NOTIFICATION_INTERVAL_MINUTES=15
``` 
# Motivate.AI Desktop Application

A comprehensive desktop companion that provides gentle nudges, task management, and AI-guided project suggestions to help you reconnect with your unfinished projects.

## 🌟 Features

### Core Functionality
- **Modern Task Management UI**: Clean, responsive interface built with CustomTkinter
- **Smart System Tray Integration**: Always accessible from the system tray
- **Intelligent Idle Monitoring**: Detects when you're inactive and provides gentle suggestions
- **Pop-up Interruption System**: Context-aware notifications that appear at optimal times
- **Quick Task Addition**: Fast task entry without opening the full interface
- **Project Organization**: Organize tasks by projects with visual project cards

### Smart Notifications
- **Gentle Nudges**: Encouraging reminders when you've been idle
- **15-Minute Suggestions**: Quick actionable tasks to get you moving
- **Progress Celebrations**: Positive reinforcement for completed tasks
- **Contextual Suggestions**: AI-powered task recommendations based on your activity

### User Experience
- **Responsive Design**: Adapts to different screen sizes and preferences
- **Quiet Hours**: Respects your sleep and focus time
- **Do Not Disturb Mode**: Temporarily disable interruptions
- **Frequency Control**: Smart limits to prevent notification fatigue

## 🏗️ Architecture

```
desktop/
├── ui/                     # User interface components
│   ├── main_window.py      # Main task management interface
│   ├── popup_manager.py    # Smart pop-up system
│   ├── quick_add.py        # Quick task addition dialog
│   └── components/         # Reusable UI components
├── services/               # Desktop services
│   ├── tray_manager.py     # System tray integration
│   ├── idle_monitor.py     # Idle detection and monitoring
│   └── speech_service.py   # Speech recognition (coming soon)
├── models/                 # Data models and state
└── main.py                # Application entry point
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Windows 10/11 (primary support)
- Backend API running (optional - works offline)

### Installation

1. **Install Dependencies**:
   ```bash
   cd desktop
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   # Copy and edit the environment file
   cp ../shared/config.env.example .env
   
   # Edit .env with your settings:
   # API_BASE_URL=http://localhost:8010/api/v1
   # IDLE_THRESHOLD_MINUTES=10
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

## 🎯 Usage

### System Tray Menu
Right-click the Motivate.AI icon in your system tray to access:

- **🏠 Open Main Window**: Full task management interface
- **➕ Quick Add Task**: Fast task entry dialog
- **🎤 Voice Add Task**: Speech-to-text task creation (coming soon)
- **⏰ Next Suggestion**: Get an immediate AI suggestion
- **📊 Today's Progress**: View your daily accomplishments
- **⚙️ Settings**: Configure preferences and behavior
- **❌ Exit**: Close the application

### Main Window Interface
- **Project Sidebar**: View and manage your projects
- **Task List**: See today's focus items with time estimates
- **Filter Options**: View today's tasks, overdue items, or all tasks
- **Progress Tracking**: Monitor daily completion statistics

### Smart Notifications
The app intelligently monitors your activity and provides:

- **Idle Nudges**: Gentle suggestions when you've been inactive
- **Task Suggestions**: Specific 15-minute tasks to make progress
- **Break Reminders**: Encouragement to take breaks during long work sessions
- **Progress Celebrations**: Positive reinforcement for completed tasks

## ⚙️ Configuration

### Idle Monitoring Settings
- **Threshold**: Set how long before you're considered idle (default: 10 minutes)
- **Intervention Frequency**: Maximum pop-ups per hour (default: 4)
- **Quiet Hours**: Set times when notifications are disabled

### Notification Preferences
- **Gentle Mode**: Use encouraging rather than demanding language
- **Do Not Disturb**: Temporarily disable all interruptions
- **Sound Notifications**: Enable/disable notification sounds

### UI Customization
- **Theme**: Light/dark mode support
- **Window Size**: Responsive design adapts to your preferences
- **Sidebar**: Collapsible project sidebar

## 🔧 Technical Details

### Dependencies
- **CustomTkinter**: Modern UI framework
- **pystray**: System tray integration
- **psutil**: System monitoring
- **requests**: API communication
- **Pillow**: Image processing for icons
- **python-dotenv**: Environment configuration

### Windows Integration
- **Native Idle Detection**: Uses Windows API for accurate idle time
- **System Notifications**: Native Windows notification system
- **Auto-start**: Optional startup integration (coming soon)

### API Integration
- **Graceful Degradation**: Works offline with demo data
- **Real-time Sync**: Automatically syncs with backend when available
- **Error Handling**: Robust error handling for network issues

## 🎤 Voice Integration (Coming Soon)

Planned speech recognition features:
- Voice commands for task creation
- Hands-free task completion
- Voice notes for project updates
- Global hotkey activation

## 🔒 Privacy & Data

- **Local Processing**: Idle monitoring and notifications happen locally
- **Minimal Data Collection**: Only syncs task data with your backend
- **No Tracking**: No usage analytics or tracking
- **Secure Communication**: HTTPS API communication

## 🚀 Roadmap

### Short Term
- [ ] Speech recognition integration
- [ ] Enhanced keyboard shortcuts
- [ ] Settings configuration UI
- [ ] Task timer functionality

### Medium Term
- [ ] Custom notification sounds
- [ ] Advanced AI suggestions
- [ ] Project templates
- [ ] Export/import functionality

### Long Term
- [ ] Cross-platform support (macOS, Linux)
- [ ] Plugin system
- [ ] Advanced analytics
- [ ] Mobile app synchronization

## 🐛 Troubleshooting

### Common Issues

**App won't start:**
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.9+)
- Check environment configuration in `.env` file

**No system tray icon:**
- Ensure system tray is enabled in Windows settings
- Check if antivirus is blocking the application
- Try running as administrator

**Notifications not working:**
- Verify Windows notification settings
- Check Do Not Disturb mode in app settings
- Confirm quiet hours configuration

**Backend connection issues:**
- Verify backend is running: check `http://localhost:8010/health`
- App works offline with demo data if backend unavailable
- Check API_BASE_URL in `.env` file

### Debug Mode
Run with debug output:
```bash
python main.py --debug
```

## 📝 Logging

Logs are written to:
- Console output (real-time)
- `logs/desktop.log` (persistent)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See the main project LICENSE file for licensing information. 
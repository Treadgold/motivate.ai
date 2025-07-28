# Motivate.AI Desktop Application

A modern desktop companion that provides task management, project organization, and system tray integration. Built with CustomTkinter for a native Windows experience.

## 🌟 Current Features (Working Now!)

### ✅ Fully Functional
- **📋 Project Management**: Create, view, and organize projects with visual cards
- **🏠 Main Window Interface**: Clean, responsive task management UI
- **🔔 System Tray Integration**: Always accessible from system tray with context menu
- **➕ New Project Creation**: Complete modal dialog with form validation and API integration
- **🔄 Real-time Updates**: Projects list refreshes automatically after creation
- **💾 Backend Integration**: Full API connectivity with graceful offline fallback
- **⚡ Lightning-Fast Startup**: Pre-created window architecture for instant response

### 🎯 System Tray Menu
Right-click the Motivate.AI icon to access:
- **🏠 Open Main Window** ✅ Working
- **➕ Quick Add Task** (Coming Soon)
- **🎤 Voice Add Task** (Planned)
- **⏰ Next Suggestion** (Planned)
- **📊 Today's Progress** (Planned)
- **⚙️ Settings** (Planned)
- **❌ Exit** ✅ Working

### 🔧 Technical Highlights
- **Thread-Safe Architecture**: Queue-based communication prevents GIL errors
- **Stable on Windows**: Tested extensively on Windows 10/11
- **Responsive UI**: No blocking operations, immediate user feedback
- **Graceful Error Handling**: Works offline with demo data when backend unavailable

## 🏗️ Architecture

```
desktop/
├── main.py                     # Application orchestrator and main loop
├── ui/                         # User interface components  
│   ├── main_window.py          # Main task management interface
│   ├── new_project.py          # Project creation dialog
│   ├── popup_manager.py        # Smart notification system
│   ├── quick_add.py            # Quick task addition dialog
│   └── components/             # Reusable UI components
├── services/                   # Background services
│   ├── tray_manager_fixed.py   # System tray with queue communication
│   ├── idle_monitor.py         # Activity monitoring (temporarily disabled)
│   └── speech_service.py       # Speech recognition (planned)
├── models/                     # Data models and state management
├── assets/                     # Icons and UI resources
└── DESIGN_GUIDE.md            # Comprehensive architecture documentation
```

## 🚀 Getting Started

### Prerequisites
- **Windows 10/11** (primary support)
- **Python 3.9 or higher**
- **Backend API** running on port 8010 (optional - works offline)

### Quick Setup

1. **Install Dependencies**:
   ```bash
   cd desktop
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your settings:
   API_BASE_URL=http://localhost:8010/api/v1
   API_PORT=8010
   IDLE_THRESHOLD_MINUTES=10
   ```

3. **Start the Application**:
   ```bash
   python main.py
   ```

4. **Access via System Tray**:
   - Look for Motivate.AI icon in system tray
   - Right-click for menu options
   - Click "🏠 Open Main Window" to start

## 🎯 How to Use

### Creating Your First Project
1. **Open Main Window**: Right-click tray icon → "🏠 Open Main Window"
2. **Click "New Project"**: Button in the top toolbar
3. **Fill Project Details**: 
   - Project title (required)
   - Description (optional) 
   - Category selection
   - Priority level
4. **Click "Create Project"**: Project appears immediately in sidebar

### Project Management
- **View Projects**: Listed in left sidebar with task counts
- **Project Cards**: Visual representation with key details
- **Automatic Updates**: List refreshes after creating new projects

### System Tray Features  
- **Always Available**: App runs in background
- **Quick Actions**: Right-click menu for common tasks
- **Silent Operation**: No unnecessary notifications

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# API Configuration
API_BASE_URL=http://localhost:8010/api/v1
API_PORT=8010

# Feature Settings
IDLE_THRESHOLD_MINUTES=10

# UI Preferences  
WINDOW_WIDTH=1000
WINDOW_HEIGHT=700
```

### Backend Integration
- **Online Mode**: Full API integration with live data sync
- **Offline Mode**: Works with demo data when backend unavailable
- **Graceful Fallback**: Automatic switching between modes
- **Error Recovery**: Robust handling of network issues

## 🔧 Technical Dependencies

### Core Libraries
- **CustomTkinter 5.2.0**: Modern UI framework for native Windows look
- **pystray 0.19.4**: System tray integration
- **requests 2.31.0**: HTTP API communication
- **python-dotenv 1.0.0**: Environment configuration
- **Pillow 10.0.0**: Image processing for UI assets
- **psutil 5.9.5**: System monitoring capabilities

### Windows Integration
- **Native UI**: CustomTkinter provides Windows 11 styling
- **System Tray**: Native Windows tray integration
- **Threading**: Windows-optimized threading model (`daemon=False`)
- **Startup Integration**: Ready for Windows startup (batch files included)

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt

# Check environment file
ls .env  # Should exist with API_BASE_URL
```

**No system tray icon:**
- Ensure Windows system tray is enabled
- Check if antivirus is blocking the application
- Try running as administrator
- Restart Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe`

**Main window won't open:**
- Check console output for error messages
- Verify CustomTkinter installation: `pip show customtkinter`
- Try running with debug: `python main.py --debug`

**Backend connection issues:**
- Verify backend is running: visit `http://localhost:8010/health`
- Check `.env` file has correct `API_BASE_URL`
- App works offline - backend connection is optional

**Project creation not working:**
- Check console for API error messages
- Verify backend `/api/v1/projects` endpoint is accessible
- Form validation errors will show in dialog

### Debug Mode
Enable detailed logging:
```bash
python main.py --debug
```

### Log Files
Check for error details:
- **Console Output**: Real-time debugging information
- **Application State**: Printed during startup sequence

## 📊 Performance & Stability

### Optimizations
- **Pre-created UI**: Main window created at startup for instant opening
- **Thread Safety**: Queue-based communication prevents GIL errors
- **Short Timeouts**: 2-second API timeouts prevent UI blocking
- **Memory Efficient**: Lightweight component architecture

### Stability Features
- **Error Recovery**: Graceful handling of component failures
- **Restart Logic**: System tray auto-restart on Windows crashes
- **Thread Isolation**: Background services don't affect GUI responsiveness
- **Resource Cleanup**: Proper shutdown handling

## 🔮 Roadmap

### Near Term (Next Releases)
- [ ] **Quick Add Task**: Fast task entry from tray menu
- [ ] **Settings Dialog**: Configure preferences via GUI
- [ ] **Task Management**: View and edit tasks within projects
- [ ] **Re-enable Idle Monitoring**: Smart activity tracking with stability fixes

### Medium Term  
- [ ] **Enhanced Project Views**: Different layouts and filtering options
- [ ] **Keyboard Shortcuts**: Global hotkeys for common actions
- [ ] **Import/Export**: Project data backup and restore
- [ ] **Custom Themes**: UI appearance customization

### Long Term
- [ ] **Cross-Platform**: macOS and Linux support
- [ ] **Voice Integration**: Speech-to-text task creation
- [ ] **Smart Suggestions**: AI-powered task recommendations
- [ ] **Mobile Sync**: Integration with mobile app (when available)

## 📚 Documentation

- **DESIGN_GUIDE.md**: Comprehensive architecture and development guide
- **API Documentation**: See backend `/docs` for API reference
- **Threading Best Practices**: Critical for Windows stability

## 🤝 Development

### Key Principles
1. **All GUI operations on main thread** (prevents GIL errors)
2. **Queue-based communication** between components
3. **Component isolation** for maintainable code
4. **Graceful degradation** when services unavailable

### Adding Features
1. Read `DESIGN_GUIDE.md` for architecture patterns
2. Follow threading guidelines strictly
3. Test on clean Windows environment
4. Ensure graceful error handling

### Testing Approach
- **Component isolation**: Test each service independently
- **Threading stress tests**: Rapid user interactions
- **API failure simulation**: Test offline behavior
- **UI responsiveness**: Measure interaction delays

## 📄 License

See the main project LICENSE file for licensing information.

---

**🎉 Status**: **Fully Functional Core Features** - Ready for daily use with project management and system tray integration! 
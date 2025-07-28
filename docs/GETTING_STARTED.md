# Getting Started with Motivate.AI

Welcome to Motivate.AI! This guide will help you set up and start using the application.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd motivate.ai
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
The backend will start on `http://localhost:8010`

### 3. Desktop App Setup
```bash
cd desktop
pip install -r requirements.txt
python main.py
```

## ✅ What's Working Now

### 🎯 New Project Creation (FULLY FUNCTIONAL!)
- **Complete project dialog** with all backend fields
- **Professional form** including:
  - Project Title (required)
  - Description (multi-line)
  - Priority (low, medium, high, urgent)
  - Estimated Time (in hours)
  - Tags (comma-separated)
  - Location
  - Next Action
- **Backend integration** with error handling
- **Automatic project list refresh** after creation

### 🖥️ Desktop Application Features
- **System tray integration** - Right-click for menu
- **Main window** with project management interface
- **Real-time API connectivity** (backend must be running)
- **Intelligent idle monitoring**
- **Smart popup notifications**
- **Offline mode** with demo data when backend unavailable

### 🛠️ Backend API Features
- **RESTful API** with FastAPI
- **SQLite database** for persistence
- **Project CRUD operations** 
- **Health check endpoint**
- **Automatic API documentation** at `/docs`

## 🎮 How to Use

### Creating Your First Project
1. **Start the backend** (`cd backend && python main.py`)
2. **Start the desktop app** (`cd desktop && python main.py`)  
3. **Right-click the system tray icon** → "Open Main Window"
4. **Click the "➕ New Project" button** in the sidebar
5. **Fill out the project form** (only title is required)
6. **Click "Create Project"** to save
7. **Watch your project appear** in the projects list!

### System Tray Features
Right-click the Motivate.AI system tray icon to access:
- 🏠 **Open Main Window** - Full project management interface
- ➕ **Quick Add Task** - (Coming soon)
- 🎤 **Voice Add Task** - (Coming soon)  
- ⏰ **Next Suggestion** - (Coming soon)
- 📊 **Today's Progress** - (Coming soon)
- ⚙️ **Settings** - (Coming soon)
- ❌ **Exit** - Close the application

## 🔧 Configuration

### Environment Variables
Both backend and desktop apps use `.env` files:

**Backend (.env):**
- `API_PORT=8010` - Backend server port
- `DATABASE_URL=sqlite:///./motivate_ai.db` - Database location

**Desktop (.env):**  
- `API_BASE_URL=http://localhost:8010/api/v1` - Backend API URL
- `IDLE_THRESHOLD_MINUTES=10` - Idle detection threshold

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'fastapi'"**
- Solution: `cd backend && pip install -r requirements.txt`

**"Backend not available - running in offline mode"**
- Ensure backend is running: `cd backend && python main.py`
- Check that port 8010 is available
- Verify `.env` files have matching ports

**"KeyError: 'name'" when opening main window**  
- This was fixed! Update to latest version
- Projects now use `"title"` field instead of `"name"`

**Cannot connect to API**
- Ensure both `.env` files use port `8010` (not 8000)
- Check Windows Firewall isn't blocking the connection
- Verify `API_BASE_URL=http://localhost:8010/api/v1` in desktop/.env

## 📚 Next Steps

### Ready to Build
- ✅ **New Project Creation** - Complete and functional
- 🔨 **Task Management** - Ready for implementation  
- 🎯 **Quick Add Tasks** - Next logical feature
- ⚙️ **Settings Dialog** - For customization
- 📱 **Mobile App** - Future expansion

### Development
- All tests pass with `python -m pytest`
- API documentation available at `http://localhost:8010/docs`
- Code follows established patterns in `/docs/PROJECT_STRUCTURE.md`

## 🎯 Current Focus: Building Core Features

The foundation is solid! The backend API works perfectly, the desktop app connects reliably, and project creation is fully functional. We're ready to expand into task management, settings, and more advanced features.

**Happy coding! 🚀** 
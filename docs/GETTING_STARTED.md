# Getting Started with Motivate.AI

Welcome to your AI-guided project companion! This guide will help you get everything set up and running.

## 🎯 What This Does

Motivate.AI helps you stay connected with your projects by:
- Tracking your projects and tasks in a simple, low-admin way
- Monitoring when you're idle and gently suggesting 15-minute actions
- Providing AI-powered suggestions based on your project context
- Working across Windows desktop and Android mobile

## 🚀 Quick Setup (Windows)

### 1. Prerequisites
- Python 3.9+ installed
- Git installed
- (Optional) Flutter SDK for mobile development

### 2. Initial Setup
```bash
# Clone or download the project
cd motivate.ai

# Run the automated setup
python scripts/setup.py
```

### 3. Start the Backend
```bash
cd backend
venv\Scripts\activate
python main.py
```

The API will be available at http://localhost:8000
Visit http://localhost:8000/docs to see the interactive API documentation.

### 4. Start the Desktop App
```bash
# In a new terminal
cd desktop
venv\Scripts\activate
python main.py
```

Look for the system tray icon in the bottom-right corner of your screen.

## 📱 Mobile Setup (Optional)

The mobile app requires Flutter. If you don't have it installed:

1. Install Flutter: https://flutter.dev/docs/get-started/install
2. Create the Flutter project:
   ```bash
   cd mobile
   flutter create . --project-name motivate_ai
   flutter pub get
   flutter run
   ```

## 💡 Your First Project

1. **Open your browser** to http://localhost:8000/docs
2. **Create a project** using the `/api/v1/projects` POST endpoint:
   ```json
   {
     "title": "Organize Workshop",
     "description": "Sort through tools and create a better workspace",
     "location": "garage workshop",
     "next_action": "Clear the workbench of old projects"
   }
   ```
3. **Let the system work**: The desktop app will start monitoring your activity
4. **Get suggestions**: When you're idle, you'll receive gentle prompts

## 🔧 Configuration

Edit the `.env` files in each component:

### Backend (`backend/.env`)
```
DATABASE_URL=sqlite:///./motivate_ai.db
DEBUG=true
```

### Desktop (`desktop/.env`)
```
API_BASE_URL=http://localhost:8000/api/v1
IDLE_THRESHOLD_MINUTES=10
NOTIFICATION_INTERVAL_MINUTES=15
```

## 🎛️ How It Works

1. **Projects**: Think of these as your major undertakings - "Rewire workshop", "Build garden shed", etc.
2. **Tasks**: Small, actionable steps that move projects forward
3. **Activity Logging**: The system tracks when you work on things
4. **AI Suggestions**: Based on your project context and current energy, get gentle nudges

## 🆘 Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Ensure virtual environment is activated
- Check for port conflicts (8000)

### Desktop app not showing
- Look for system tray icon
- Check if Python virtual environment has GUI packages
- Try running from command line to see error messages

### Database issues
- Delete `backend/motivate_ai.db` to start fresh
- Check file permissions

## 🎨 Customization

### Adding Your Own AI
Replace the hardcoded suggestions in `backend/api/suggestions.py` with:
- OpenAI API calls
- Local LLM integration
- Custom logic based on your work patterns

### Notification Styles
Modify `desktop/notifications.py` to change:
- Notification appearance
- Sound alerts
- Timing patterns

## 🔮 Next Steps

Once you have the basic system running:
1. Add real AI integration for smarter suggestions
2. Implement voice note recording
3. Add project photos and progress tracking
4. Create smart scheduling based on your energy patterns
5. Integrate with your existing tools (calendars, task managers)

## 🤝 Need Help?

This system is designed to grow with you. Start simple:
1. Add one real project
2. Let it monitor for a day
3. See what suggestions feel helpful
4. Gradually add more projects and customize the prompts

Remember: The goal isn't productivity optimization - it's gentle reconnection with the things you care about building. 
# Mobile App - Flutter Android Application

A Flutter mobile app for managing projects and receiving motivation prompts on the go.

## 🚀 Setup

1. Install Flutter SDK: https://flutter.dev/docs/get-started/install
2. Verify installation: `flutter doctor`
3. Navigate to mobile directory: `cd mobile`
4. Install dependencies: `flutter pub get`

## 🏃 Running

### Development
```bash
flutter run
```

### Build APK
```bash
flutter build apk --release
```

## ✨ Features

- **Project Management**: View and edit projects
- **Task Management**: Track tasks and mark completed
- **Push Notifications**: Receive motivation prompts
- **Offline Support**: Basic functionality without internet
- **Voice Notes**: Record quick project notes

## 📁 Structure

```
mobile/
├── lib/
│   ├── main.dart            # App entry point
│   ├── screens/            # UI screens
│   ├── widgets/            # Reusable components
│   ├── models/             # Data models
│   ├── services/           # API and local services
│   └── utils/              # Helper functions
├── android/                # Android-specific code
├── pubspec.yaml           # Dependencies
└── README.md              # This file
```

## 🔧 Configuration

Update `lib/config/api_config.dart`:
```dart
const String API_BASE_URL = 'http://your-backend-url:8000/api/v1';
```

For local development, use your computer's IP address instead of localhost. 
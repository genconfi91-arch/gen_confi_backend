# Login API Testing Guide

## 🚀 Server Status

The backend server is starting. Once running, you can test the login API.

## 📡 Login API Endpoint

### Endpoint Details
- **URL**: `http://localhost:8000/api/v1/auth/login`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Request Body
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Success Response (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "phone": "1234567890",
    "role": "client"
  }
}
```

### Error Response (401 Unauthorized)
```json
{
  "detail": "Invalid email or password"
}
```

## 🧪 Test with cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

## 📱 Flutter App Configuration

### Update API Base URL

In your Flutter app, update `lib/core/constants/api_constants.dart`:

**For Android Emulator:**
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
```

**For iOS Simulator:**
```dart
static const String baseUrl = 'http://localhost:8000/api/v1';
```

**For Physical Device:**
```dart
// Use your computer's IP address
static const String baseUrl = 'http://192.168.1.XXX:8000/api/v1';
```

### Test Login in Flutter

```dart
// In your login screen
final authNotifier = ref.read(authProvider.notifier);
final success = await authNotifier.login(email, password);

if (success) {
  // Navigate to home
  Navigator.pushReplacementNamed(context, '/home');
} else {
  // Show error
  final error = ref.read(authErrorProvider);
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(error ?? 'Login failed')),
  );
}
```

## 🔍 Verify Server is Running

1. **Check Health Endpoint:**
   ```powershell
   curl http://localhost:8000/health
   ```

2. **Open Swagger UI:**
   - Browser: http://localhost:8000/docs
   - Test login directly in the browser

3. **Check Server Logs:**
   - Look for: "Uvicorn running on http://0.0.0.0:8000"

## ⚠️ Troubleshooting

### Server Not Starting
1. Check if port 8000 is available
2. Verify database connection: `python -m app.db.test_connection`
3. Check .env file exists and has correct DATABASE_URL

### Login Fails
1. Verify user exists in database
2. Check password is correct
3. Verify API base URL in Flutter app matches server

### Network Error in Flutter
1. For Android Emulator: Use `10.0.2.2` instead of `localhost`
2. For Physical Device: Use your computer's IP address
3. Ensure backend server is running
4. Check firewall settings

## 📋 Quick Test Checklist

- [ ] Backend server is running
- [ ] Database connection works
- [ ] Health endpoint responds
- [ ] Swagger UI accessible
- [ ] Flutter app API base URL configured
- [ ] Test login with Swagger UI first
- [ ] Then test from Flutter app


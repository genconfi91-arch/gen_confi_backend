# Mobile App Authentication Guide

## Current API Endpoints

### Authentication APIs (`/api/v1/auth`)

1. **POST `/api/v1/auth/signup`** - Register new user
   - Returns: `access_token`, `token_type`, `user`
   
2. **POST `/api/v1/auth/login`** - Login user
   - Returns: `access_token`, `token_type`, `user`
   
3. **GET `/api/v1/auth/me`** - Get current user (requires token)
   - Headers: `Authorization: Bearer <token>`

### User Management APIs (`/api/v1/users`)

4. **POST `/api/v1/users/`** - Create user
5. **GET `/api/v1/users/`** - List users (with pagination)
6. **GET `/api/v1/users/{id}`** - Get user by ID
7. **PUT `/api/v1/users/{id}`** - Update user
8. **DELETE `/api/v1/users/{id}`** - Delete user

---

## Mobile App Token Implementation

### How JWT Tokens Work for Mobile

1. **User logs in** → Backend returns JWT token
2. **Mobile app stores token** → Save in secure storage (SharedPreferences/Keychain)
3. **App makes API calls** → Include token in `Authorization` header
4. **Token validation** → Backend verifies token on each request
5. **Token expires** → App should refresh or re-login

### Current Token Settings

- **Token Expiration**: 30 minutes (configurable in `.env`)
- **Token Type**: JWT (JSON Web Token)
- **Algorithm**: HS256

---

## Implementation Steps for Mobile App

### 1. Store Token Securely

#### Flutter (Dart) Example:
```dart
import 'package:shared_preferences/shared_preferences.dart';

class TokenStorage {
  static const String _tokenKey = 'access_token';
  static const String _userKey = 'user_data';
  
  // Save token after login
  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }
  
  // Get stored token
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }
  
  // Save user data
  static Future<void> saveUser(Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user));
  }
  
  // Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
  
  // Clear token on logout
  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }
}
```

#### Android (Kotlin) Example:
```kotlin
class TokenManager(context: Context) {
    private val prefs = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
    
    fun saveToken(token: String) {
        prefs.edit().putString("access_token", token).apply()
    }
    
    fun getToken(): String? {
        return prefs.getString("access_token", null)
    }
    
    fun isLoggedIn(): Boolean {
        return getToken() != null
    }
    
    fun clearToken() {
        prefs.edit().remove("access_token").apply()
    }
}
```

#### iOS (Swift) Example:
```swift
import Security

class TokenManager {
    static let shared = TokenManager()
    private let tokenKey = "access_token"
    
    func saveToken(_ token: String) {
        KeychainHelper.save(token, forKey: tokenKey)
    }
    
    func getToken() -> String? {
        return KeychainHelper.load(forKey: tokenKey)
    }
    
    func isLoggedIn() -> Bool {
        return getToken() != nil
    }
    
    func clearToken() {
        KeychainHelper.delete(forKey: tokenKey)
    }
}
```

### 2. Make Authenticated API Calls

#### Flutter Example:
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://your-api-url.com/api/v1';
  
  // Get headers with token
  static Future<Map<String, String>> getHeaders() async {
    final token = await TokenStorage.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }
  
  // Login
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Save token
      await TokenStorage.saveToken(data['access_token']);
      await TokenStorage.saveUser(data['user']);
      return data;
    } else {
      throw Exception('Login failed');
    }
  }
  
  // Get current user
  static Future<Map<String, dynamic>> getCurrentUser() async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
      // Token expired, need to re-login
      await TokenStorage.clearToken();
      throw Exception('Session expired');
    } else {
      throw Exception('Failed to get user');
    }
  }
}
```

### 3. Check Login Status on App Start

#### Flutter Example:
```dart
class AuthService {
  static Future<bool> checkAuthStatus() async {
    final isLoggedIn = await TokenStorage.isLoggedIn();
    if (isLoggedIn) {
      // Verify token is still valid
      try {
        await ApiService.getCurrentUser();
        return true;
      } catch (e) {
        // Token invalid, clear it
        await TokenStorage.clearToken();
        return false;
      }
    }
    return false;
  }
}

// In your main app
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Check if user is logged in
  final isLoggedIn = await AuthService.checkAuthStatus();
  
  runApp(MyApp(isLoggedIn: isLoggedIn));
}
```

### 4. Handle Token Expiration

When token expires (401 Unauthorized), you have two options:

**Option A: Auto Re-login** (if you store credentials - not recommended)
```dart
// Not recommended for security reasons
```

**Option B: Redirect to Login** (Recommended)
```dart
// In your API interceptor
if (response.statusCode == 401) {
  await TokenStorage.clearToken();
  // Navigate to login screen
  Navigator.pushReplacementNamed(context, '/login');
}
```

---

## Recommended Backend Changes for Mobile

### 1. Increase Token Expiration for Mobile

Update `.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days (for mobile apps)
```

Or create separate expiration for mobile:
- Short-lived tokens (30 min) for web
- Long-lived tokens (30 days) for mobile

### 2. Add Refresh Token Endpoint (Recommended)

This allows refreshing tokens without re-login. See implementation below.

---

## API Request Examples

### Login Request
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Login Response
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

### Authenticated Request
```bash
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Best Practices

1. **Store token securely** - Use Keychain (iOS) or EncryptedSharedPreferences (Android)
2. **Never store password** - Only store the token
3. **Handle token expiration** - Check 401 responses and redirect to login
4. **Validate token on app start** - Call `/auth/me` to verify token is valid
5. **Clear token on logout** - Remove token from storage
6. **Use HTTPS** - Always use HTTPS in production
7. **Token refresh** - Implement refresh token mechanism for better UX

---

## Mobile App Flow

```
App Start
    ↓
Check if token exists
    ↓
Yes → Call /auth/me to verify
    ↓
Token valid? → Yes → User logged in (skip login)
    ↓
No → Clear token → Show login screen
```

---

## Next Steps

1. Implement token storage in your mobile app
2. Add API service with token headers
3. Check auth status on app start
4. Handle token expiration gracefully
5. Consider implementing refresh tokens (see backend implementation)


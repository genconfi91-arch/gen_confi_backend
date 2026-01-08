# API Summary - Gen Confi Backend

## Base URL
```
http://localhost:8000/api/v1
```

---

## 🔐 Authentication APIs (`/api/v1/auth`)

### 1. POST `/api/v1/auth/signup`
**Register a new user**

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "1234567890",
    "role": "client"
  }
}
```

---

### 2. POST `/api/v1/auth/login`
**Login user**

**Request:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "1234567890",
    "role": "client"
  }
}
```

---

### 3. GET `/api/v1/auth/me`
**Get current authenticated user**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "phone": "1234567890",
  "role": "client"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

---

## 👥 User Management APIs (`/api/v1/users`)

### 4. POST `/api/v1/users/`
**Create a new user**

**Request:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "phone": "1234567890",
  "role": "client"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "phone": "1234567890",
  "role": "client"
}
```

---

### 5. GET `/api/v1/users/`
**Get all users with pagination**

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 1000) - Maximum records to return

**Example:**
```
GET /api/v1/users/?skip=0&limit=10
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "name": "User One",
    "phone": "1234567890",
    "role": "client"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "name": "User Two",
    "phone": "0987654321",
    "role": "expert"
  }
]
```

---

### 6. GET `/api/v1/users/{user_id}`
**Get user by ID**

**Path Parameters:**
- `user_id` (int) - User ID

**Example:**
```
GET /api/v1/users/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "phone": "1234567890",
  "role": "client"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "User with ID 1 not found"
}
```

---

### 7. PUT `/api/v1/users/{user_id}`
**Update user**

**Path Parameters:**
- `user_id` (int) - User ID

**Request (all fields optional):**
```json
{
  "email": "newemail@example.com",
  "name": "New Name",
  "phone": "9876543210",
  "role": "expert"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "name": "New Name",
  "phone": "9876543210",
  "role": "expert"
}
```

---

### 8. DELETE `/api/v1/users/{user_id}`
**Delete user**

**Path Parameters:**
- `user_id` (int) - User ID

**Response (204 No Content):**
No body

**Error (404 Not Found):**
```json
{
  "detail": "User with ID 1 not found"
}
```

---

## 🏠 Root Endpoints

### 9. GET `/`
**Root endpoint**

**Response (200 OK):**
```json
{
  "message": "Welcome to FastAPI PostgreSQL API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 10. GET `/health`
**Health check**

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## 📊 Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/signup` | ❌ | Register new user |
| POST | `/api/v1/auth/login` | ❌ | Login user |
| GET | `/api/v1/auth/me` | ✅ | Get current user |
| POST | `/api/v1/users/` | ❌ | Create user |
| GET | `/api/v1/users/` | ❌ | List users |
| GET | `/api/v1/users/{id}` | ❌ | Get user by ID |
| PUT | `/api/v1/users/{id}` | ❌ | Update user |
| DELETE | `/api/v1/users/{id}` | ❌ | Delete user |
| GET | `/` | ❌ | Root endpoint |
| GET | `/health` | ❌ | Health check |

**Total: 10 endpoints**

---

## 🔑 Authentication

### How to Use Tokens

1. **Login/Signup** → Get `access_token` from response
2. **Store token** → Save in mobile app secure storage
3. **Make requests** → Include in `Authorization` header:
   ```
   Authorization: Bearer <access_token>
   ```
4. **Token expires** → Current: 30 minutes (configurable)

### Token Expiration

- **Current**: 30 minutes (set in `.env` as `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **For Mobile**: Recommended to increase to 7-30 days
- **Update `.env`**:
  ```env
  ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days
  ```

---

## 📱 Mobile App Integration

See `MOBILE_AUTH_GUIDE.md` for:
- Token storage implementation
- API call examples
- Auto-login flow
- Token expiration handling

---

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🧪 Testing with cURL

### Login Example
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```


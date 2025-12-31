# FastAPI PostgreSQL API

Enterprise-grade FastAPI backend with PostgreSQL, built using clean architecture principles.

## 🏗️ Architecture

This project follows **Clean Architecture** with strict separation of concerns:

```
app/
├── core/          # Core configuration, security, logging
├── db/            # Database setup and session management
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic schemas for validation
├── repositories/  # Data access layer (Repository pattern)
├── services/      # Business logic layer
├── api/           # API endpoints and routing
├── utils/         # Utility functions
└── tests/         # Test files
```

### Layer Responsibilities

- **Models**: Database table definitions using SQLAlchemy
- **Schemas**: Request/response validation using Pydantic
- **Repositories**: Database operations (CRUD)
- **Services**: Business logic and orchestration
- **API**: HTTP endpoints and request handling

## 📋 Requirements

- Python 3.11+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd Gen_Confi_Backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and configure it:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and set your database connection:

```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/gen_confi
SECRET_KEY=your-secret-key-here-minimum-32-characters-long
```

### 5. Setup Database

Create a PostgreSQL database:

```sql
CREATE DATABASE gen_confi;
```

**Note:** Ensure PostgreSQL is running locally with:
- Username: `postgres`
- Password: `root`
- Port: `5432`

### 6. Test Database Connection

Before running the application, test the database connection:

```bash
python -m app.db.test_connection
```

This will verify:
- PostgreSQL connection is working
- Database `gen_confi` exists and is accessible
- Credentials are correct

### 7. Initialize Database (Development)

For development, you can auto-create tables:

```bash
python -m app.db.init_db
```

**For production**, use Alembic migrations:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 8. Verify Connection in pgAdmin

To verify the database connection in pgAdmin:

1. **Open pgAdmin** and connect to your local PostgreSQL server:
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: `root`

2. **Navigate to Databases** → `gen_confi`

3. **Check Tables**:
   - After running `python -m app.db.init_db`, you should see the `users` table
   - Expand `gen_confi` → `Schemas` → `public` → `Tables`

4. **Verify Table Structure**:
   - Right-click on `users` table → `View/Edit Data` → `All Rows`
   - Check columns: `id`, `email`, `name`

5. **Test Query**:
   ```sql
   SELECT * FROM users;
   ```

### 9. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Folder Structure Explained

### `app/core/`
Core application configuration and utilities:
- **config.py**: Environment-based settings using Pydantic
- **security.py**: Password hashing, JWT token management
- **logging.py**: Centralized logging configuration

### `app/db/`
Database connection and session management:
- **base.py**: SQLAlchemy declarative base
- **session.py**: Database engine and session factory
- **init_db.py**: Development database initialization

### `app/models/`
SQLAlchemy ORM models representing database tables:
- **user.py**: User model with id, email, name

### `app/schemas/`
Pydantic schemas for request/response validation:
- **user.py**: UserCreate, UserUpdate, UserResponse schemas

### `app/repositories/`
Data access layer implementing Repository pattern:
- **user_repository.py**: Database operations for users (CRUD)

### `app/services/`
Business logic layer:
- **user_service.py**: User business logic, validation, error handling

### `app/api/`
API endpoints and routing:
- **deps.py**: Dependency injection for database sessions
- **v1/api.py**: API v1 router configuration
- **v1/endpoints/users.py**: User CRUD endpoints

### `app/utils/`
Utility functions:
- **pagination.py**: Pagination helpers for list endpoints

### `app/tests/`
Test files:
- **test_users.py**: Unit and integration tests for user endpoints

## 🔌 API Endpoints

### Users

- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Health & Info

- `GET /` - Root endpoint
- `GET /health` - Health check

## 📝 Example Requests

### Create User

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "name": "John Doe"
  }'
```

### Get All Users

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10"
```

### Get User by ID

```bash
curl -X GET "http://localhost:8000/api/v1/users/1"
```

### Update User

```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated"
  }'
```

### Delete User

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1"
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest app/tests/
```

## 🔄 Database Migrations

### Create a Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## 🔒 Security Features

- Password hashing using bcrypt
- JWT token support (configured but not implemented in user endpoints)
- CORS middleware configuration
- Environment-based secret management
- Input validation using Pydantic

## 🛠️ Development

### Code Style

- Type hints everywhere
- Strict separation of concerns
- Repository pattern for data access
- Service layer for business logic
- Dependency injection for database sessions

### Adding New Features

1. **Model**: Create SQLAlchemy model in `app/models/`
2. **Schema**: Create Pydantic schemas in `app/schemas/`
3. **Repository**: Create repository in `app/repositories/`
4. **Service**: Create service in `app/services/`
5. **Endpoint**: Create endpoint in `app/api/v1/endpoints/`
6. **Router**: Register in `app/api/v1/api.py`

## 📦 Dependencies

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database (via psycopg2-binary)
- **Alembic**: Database migration tool
- **Pydantic**: Data validation
- **python-jose**: JWT token handling
- **passlib**: Password hashing

## 🚨 Environment Variables

Required environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT (minimum 32 characters)
- `DEBUG`: Enable debug mode (True/False)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Follow clean architecture principles
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation as needed

## 📄 License

This project is part of the GenConfi application.

#   g e n _ c o n f i _ b a c k e n d  
 
# Project Structure

## Directory Overview

```
Gen_Confi_Backend/
├── app/                    # Main application package
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Core configuration and utilities
│   │   ├── config.py      # Environment-based settings
│   │   ├── security.py    # JWT & password hashing
│   │   └── logging.py     # Logging configuration
│   ├── db/                # Database layer
│   │   ├── base.py        # SQLAlchemy declarative base
│   │   ├── session.py     # Database engine & session
│   │   ├── init_db.py     # Development DB initialization
│   │   └── test_connection.py  # Connection test utility
│   ├── models/           # SQLAlchemy ORM models
│   │   └── user.py       # User model
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py       # User request/response schemas
│   │   └── auth.py      # Authentication schemas
│   ├── repositories/     # Data access layer
│   │   └── user_repository.py  # User CRUD operations
│   ├── services/        # Business logic layer
│   │   ├── user_service.py    # User business logic
│   │   └── auth_service.py    # Authentication logic
│   ├── api/             # API endpoints
│   │   ├── deps.py      # Dependency injection
│   │   └── v1/          # API version 1
│   │       ├── api.py   # Router aggregator
│   │       └── endpoints/
│   │           ├── users.py  # User endpoints
│   │           └── auth.py  # Auth endpoints
│   ├── utils/           # Utility functions
│   │   └── pagination.py  # Pagination helpers
│   └── tests/           # Test files
│       └── test_users.py
├── alembic/             # Database migrations
│   ├── env.py          # Alembic environment
│   ├── script.py.mako  # Migration template
│   └── versions/       # Migration files
├── venv/               # Virtual environment (gitignored)
├── .env                # Environment variables (gitignored)
├── .gitignore          # Git ignore rules
├── alembic.ini         # Alembic configuration
├── requirements.txt    # Python dependencies
├── env.example         # Environment template
├── README.md           # Project documentation
├── CONTRIBUTING.md     # Contribution guidelines
└── PROJECT_STRUCTURE.md # This file
```

## Layer Responsibilities

### API Layer (`app/api/`)
- **Purpose**: HTTP request/response handling
- **Responsibilities**:
  - Route definitions
  - Request validation
  - Dependency injection
  - HTTP status codes
- **No**: Business logic, database queries

### Service Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Business rules
  - Validation
  - Error handling
  - Data transformation
- **No**: Direct database queries, HTTP concerns

### Repository Layer (`app/repositories/`)
- **Purpose**: Data access abstraction
- **Responsibilities**:
  - CRUD operations
  - Database queries
  - Transaction management
- **No**: Business logic, HTTP concerns

### Model Layer (`app/models/`)
- **Purpose**: Database table definitions
- **Responsibilities**:
  - SQLAlchemy ORM models
  - Table structure
  - Relationships
- **No**: Business logic, API concerns

### Schema Layer (`app/schemas/`)
- **Purpose**: Request/response validation
- **Responsibilities**:
  - Pydantic models
  - Data validation
  - Serialization
- **No**: Database operations, business logic

## File Naming Conventions

- **Models**: `snake_case.py` (e.g., `user.py`)
- **Schemas**: `snake_case.py` (e.g., `user.py`)
- **Repositories**: `{model}_repository.py` (e.g., `user_repository.py`)
- **Services**: `{model}_service.py` (e.g., `user_service.py`)
- **Endpoints**: `snake_case.py` (e.g., `users.py`, `auth.py`)

## Adding New Features

When adding a new feature (e.g., "Product"):

1. Create model: `app/models/product.py`
2. Create schemas: `app/schemas/product.py`
3. Create repository: `app/repositories/product_repository.py`
4. Create service: `app/services/product_service.py`
5. Create endpoints: `app/api/v1/endpoints/products.py`
6. Register router in `app/api/v1/api.py`
7. Create migration: `alembic revision --autogenerate -m "Add products"`

## Key Files

### Entry Point
- `app/main.py` - FastAPI application initialization

### Configuration
- `app/core/config.py` - Environment-based settings
- `.env` - Environment variables (not in git)

### Database
- `app/db/session.py` - Database connection
- `app/db/base.py` - SQLAlchemy base
- `alembic/` - Database migrations

### Utilities
- `app/utils/pagination.py` - Pagination helpers
- `app/db/test_connection.py` - Connection testing

## Best Practices

1. **Keep layers separate** - Don't mix concerns
2. **Use type hints** - All functions should have types
3. **Document code** - Use docstrings
4. **Handle errors** - Use appropriate exceptions
5. **Test code** - Write tests for new features
6. **Follow conventions** - Use established patterns


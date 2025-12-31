# Contributing to Gen Confi Backend

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Git

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Gen_Confi_Backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy env.example .env  # Windows
   cp env.example .env    # Linux/Mac
   ```
   Edit `.env` with your database credentials.

5. **Test database connection**
   ```bash
   python -m app.db.test_connection
   ```

6. **Initialize database (development)**
   ```bash
   python -m app.db.init_db
   ```

7. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Code Structure

```
app/
├── core/          # Configuration, security, logging
├── db/            # Database setup and session management
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response schemas
├── repositories/  # Data access layer (Repository pattern)
├── services/      # Business logic layer
├── api/           # API endpoints and routing
├── utils/         # Utility functions
└── tests/         # Test files
```

## Coding Standards

### Architecture Principles

1. **Separation of Concerns**
   - API layer: HTTP request/response handling only
   - Service layer: Business logic and validation
   - Repository layer: Database operations only
   - Models: Database table definitions

2. **Type Hints**
   - All functions must have type hints
   - Use `Optional[T]` for nullable values
   - Use `List[T]` for lists

3. **Error Handling**
   - Use `HTTPException` for API errors
   - Log errors appropriately
   - Provide meaningful error messages

4. **Documentation**
   - Docstrings for all functions and classes
   - Use Google-style docstrings
   - Include parameter and return type descriptions

### Code Style

- Follow PEP 8 style guide
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Keep functions focused and small
- No hardcoded values - use configuration

### Adding New Features

1. **Create Model** (`app/models/`)
   ```python
   class NewModel(Base):
       __tablename__ = "new_table"
       # fields
   ```

2. **Create Schema** (`app/schemas/`)
   ```python
   class NewModelCreate(BaseModel):
       # fields
   ```

3. **Create Repository** (`app/repositories/`)
   ```python
   class NewModelRepository:
       # CRUD operations
   ```

4. **Create Service** (`app/services/`)
   ```python
   class NewModelService:
       # Business logic
   ```

5. **Create Endpoint** (`app/api/v1/endpoints/`)
   ```python
   @router.post("/")
   def create_new_model(...):
       # Endpoint logic
   ```

6. **Register Router** (`app/api/v1/api.py`)
   ```python
   api_router.include_router(new_model.router, prefix="/new-models")
   ```

7. **Create Migration** (if needed)
   ```bash
   alembic revision --autogenerate -m "Add new_model table"
   alembic upgrade head
   ```

## Testing

### Running Tests
```bash
pytest app/tests/
```

### Writing Tests
- Place tests in `app/tests/`
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

## Database Migrations

### Creating a Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations
```bash
alembic upgrade head
```

### Rolling Back
```bash
alembic downgrade -1
```

## Git Workflow

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. Push and create pull request
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Code Review Checklist

- [ ] Code follows architecture principles
- [ ] Type hints are present
- [ ] Docstrings are complete
- [ ] No hardcoded values
- [ ] Error handling is appropriate
- [ ] Tests are included (if applicable)
- [ ] No unused imports or code
- [ ] Follows PEP 8 style guide

## Common Issues

### Database Connection Issues
- Verify PostgreSQL is running
- Check `.env` file configuration
- Test connection: `python -m app.db.test_connection`

### Import Errors
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Migration Issues
- Check Alembic version: `alembic current`
- Review migration files in `alembic/versions/`

## Getting Help

- Check the README.md for detailed documentation
- Review existing code for examples
- Check FastAPI documentation: https://fastapi.tiangolo.com/
- Check SQLAlchemy documentation: https://docs.sqlalchemy.org/


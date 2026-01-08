from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_schema():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    columns = inspector.get_columns('users')
    print("Columns in 'users' table:")
    for column in columns:
        print(f"- {column['name']} ({column['type']})")

if __name__ == "__main__":
    check_schema()

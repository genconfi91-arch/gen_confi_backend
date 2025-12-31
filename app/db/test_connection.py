"""
Database connection test utility.
Use this to verify PostgreSQL connection before running the application.
"""
from sqlalchemy import text
from app.db.session import engine
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_connection() -> bool:
    """
    Test database connection by executing a simple query.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info("Database connection successful!")
            logger.info(f"  PostgreSQL version: {version}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_database_exists() -> bool:
    """
    Test if the database exists and is accessible.
    
    Returns:
        True if database exists, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            logger.info(f"Connected to database: {db_name}")
            return True
    except Exception as e:
        logger.error(f"Database access failed: {e}")
        logger.error("  Make sure the database 'gen_confi' exists.")
        logger.error("  Run: CREATE DATABASE gen_confi;")
        return False


if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    print("-" * 50)
    
    if test_connection():
        test_database_exists()
        print("-" * 50)
        print("[SUCCESS] All connection tests passed!")
    else:
        print("-" * 50)
        print("[ERROR] Connection test failed!")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check DATABASE_URL in .env file")
        print("3. Verify credentials (username: postgres, password: root)")
        print("4. Ensure database 'gen_confi' exists")


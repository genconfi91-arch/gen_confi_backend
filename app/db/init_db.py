"""
Database initialization script.
Creates tables for development purposes.
"""
from app.db.session import init_db
from app.db.base import Base
from app.core.logging import get_logger

# Import all models to ensure they're registered with Base
from app.models import user  # noqa: F401

logger = get_logger(__name__)


def init_database() -> None:
    """
    Initialize the database by creating all tables.
    This is for development only. Use Alembic for production migrations.
    """
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    init_database()


"""
Database configuration and setup
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from config import settings
from models import Base

logger = logging.getLogger(__name__)

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def init_db():
    """Initialize database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")


def get_db() -> Session:
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all():
    """Drop all tables (use with caution!)"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ All tables have been dropped")


def reset_db():
    """Reset database (drop and recreate)"""
    logger.warning("Resetting database...")
    drop_all()
    init_db()
    logger.info("✅ Database reset complete")


class DatabaseManager:
    """Database manager utilities"""

    @staticmethod
    def get_db_url() -> str:
        """Get database URL"""
        return settings.DATABASE_URL

    @staticmethod
    def get_engine():
        """Get database engine"""
        return engine

    @staticmethod
    def get_session_local():
        """Get session factory"""
        return SessionLocal

    @staticmethod
    def check_connection() -> bool:
        """Check database connection"""
        try:
            with engine.connect() as conn:
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False

    @staticmethod
    def get_db_stats():
        """Get database statistics"""
        try:
            db = SessionLocal()
            # Import models to count
            from models import User, Task, Conversation, ProcessedFile

            stats = {
                "users": db.query(User).count(),
                "tasks": db.query(Task).count(),
                "conversations": db.query(Conversation).count(),
                "files": db.query(ProcessedFile).count(),
            }
            db.close()
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return None

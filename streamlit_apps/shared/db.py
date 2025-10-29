"""
Database connection and session management.

This module provides database utilities using SQLAlchemy.
Follows Principle 4: Separation of Concerns - Data layer isolated.

Usage:
    from shared.db import get_session, init_database

    # Initialize database (run once at startup)
    init_database()

    # Get session for queries
    with get_session() as session:
        results = session.query(MyModel).all()

Configuration:
    Local: Uses DATABASE_URL from .env (default: localhost:5432)
    Server: Change DATABASE_URL to point to VM 100 (192.168.1.101:5432)
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import datetime
from typing import Generator
import logging

from shared.config import get_config

logger = logging.getLogger(__name__)

# SQLAlchemy Base for models
Base = declarative_base()


# Database Models
# These are the actual database tables

class AIInteractionLogDB(Base):
    """
    Database table for AI interaction logs.

    Stores every AI call for auditing, debugging, and analysis.
    """
    __tablename__ = "ai_interaction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String(36), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    environment = Column(String(20), nullable=False, index=True)


# Database Engine and Session
_engine = None
_SessionLocal = None


def get_engine():
    """
    Get or create database engine (singleton pattern).

    Returns:
        Engine: SQLAlchemy engine connected to PostgreSQL
    """
    global _engine
    if _engine is None:
        config = get_config()
        logger.info(f"Creating database engine: {config.database_url.split('@')[0]}@...")

        _engine = create_engine(
            config.database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,         # Connection pool size
            max_overflow=10,     # Max overflow connections
            echo=False,          # Set to True for SQL query logging
        )

        logger.info("Database engine created successfully")

    return _engine


def get_session_factory():
    """
    Get or create session factory (singleton pattern).

    Returns:
        sessionmaker: SQLAlchemy session factory
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Session factory created successfully")

    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup.

    This is a context manager that ensures proper session lifecycle:
    - Creates session
    - Commits on success
    - Rolls back on error
    - Always closes session

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        >>> from shared.db import get_session
        >>> with get_session() as session:
        ...     user = session.query(User).first()
        ...     print(user.name)
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_database():
    """
    Initialize database - create all tables.

    Run this once when setting up a new environment.
    Safe to run multiple times (won't recreate existing tables).

    Example:
        >>> from shared.db import init_database
        >>> init_database()
        Database initialized successfully
    """
    try:
        engine = get_engine()
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Verify connection
        with get_session() as session:
            # Simple query to test connection
            result = session.execute("SELECT 1")
            logger.info("Database connection verified")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        >>> from shared.db import test_connection
        >>> if test_connection():
        ...     print("Database is ready!")
        ... else:
        ...     print("Cannot connect to database")
    """
    try:
        with get_session() as session:
            session.execute("SELECT 1")
        logger.info("Database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database connection test: FAILED - {e}")
        return False


# Utility functions for common operations

def log_ai_interaction(
    call_id: str,
    provider: str,
    model: str,
    prompt: str,
    response: str | None,
    success: bool,
    error_message: str | None = None,
    latency_ms: int | None = None,
    environment: str | None = None,
) -> None:
    """
    Log an AI interaction to the database.

    Args:
        call_id: Unique identifier for this call
        provider: AI provider (mock, ollama, openai)
        model: Model name
        prompt: User prompt
        response: AI response (JSON string)
        success: Whether call succeeded
        error_message: Error message if failed
        latency_ms: Response time in milliseconds
        environment: Environment where call was made

    Example:
        >>> log_ai_interaction(
        ...     call_id="abc-123",
        ...     provider="mock",
        ...     model="mock-model",
        ...     prompt="What is 2+2?",
        ...     response='{"answer": "4"}',
        ...     success=True,
        ...     latency_ms=50
        ... )
    """
    try:
        if environment is None:
            config = get_config()
            environment = config.environment

        with get_session() as session:
            log_entry = AIInteractionLogDB(
                call_id=call_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=response,
                success=success,
                error_message=error_message,
                latency_ms=latency_ms,
                environment=environment,
            )
            session.add(log_entry)

        logger.debug(f"Logged AI interaction: {call_id}")

    except Exception as e:
        # Don't fail the app if logging fails
        logger.error(f"Failed to log AI interaction: {e}")

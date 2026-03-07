"""
Async Database Session Management Module For WattPay Application.
"""
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError
from api.common.log.logging import get_logger
from api.common.config_manager import config

# Load environment variables from .env file for backward compatibility
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / '.env'
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        logger = get_logger(__name__)
        logger.info(".env file found and loaded successfully")
        logger.debug("Loaded environment variables from %s", env_file)
except ImportError:
    # python-dotenv is not installed; skip loading .env file
    pass

logger = get_logger(__name__)


class DbSessionFactory:
    """Factory class for creating async database sessions with
    connection pooling."""

    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def _get_engine(cls) -> AsyncEngine:
        """Return or create a shared async engine (singleton)."""
        if cls._engine is None:
            db_url = cls.get_database_url()
            db_config = config.database
            host = db_url.split('@')[1] if '@' in db_url else 'localhost'
            logger.debug("Creating async engine for database at %s", host)

            cls._engine = create_async_engine(
                db_url,
                echo=False,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=db_config.pool_size,
                max_overflow=db_config.pool_overflow,
                pool_timeout=db_config.pool_timeout,
            )
        return cls._engine

    @classmethod
    def _get_session_factory(cls) -> async_sessionmaker[AsyncSession]:
        """Return or create a shared async session factory (singleton)."""
        if cls._session_factory is None:
            engine = cls._get_engine()
            cls._session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.debug("Async session factory created successfully.")
        return cls._session_factory

    @classmethod
    async def create_session(cls) -> AsyncSession:
        """Create and return a new async database session."""
        try:
            factory = cls._get_session_factory()
            session = factory()  # pylint: disable=not-callable
            logger.debug("Async database session created successfully.")
            return session

        except OperationalError as e:
            logger.error(
                "Operational error connecting to the database: %s", e
            )
            logger.error(
                "Please check if database server is running and accessible."
            )
            raise
        except DatabaseError as e:
            logger.error("Database error: %s", e)
            logger.error(
                "Please verify your database configuration settings."
            )
            raise
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error: %s", e)
            raise
        except (OSError, IOError, ValueError) as e:
            logger.error("Configuration or connection error: %s", e)
            raise

    @staticmethod
    async def test_connectivity() -> None:
        """Test database connectivity by executing a simple query."""
        engine = DbSessionFactory._get_engine()
        try:
            async with engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("Database connectivity test succeeded.")
                else:
                    logger.error("Database connectivity test failed.")
                    raise RuntimeError("Failed to execute test query.")
        except (SQLAlchemyError, OperationalError, DatabaseError) as e:
            logger.error("Error during connectivity test: %s", e)
            raise

    @staticmethod
    def get_database_url() -> str:
        """Construct and return the database URL from configuration."""
        db_config = config.database
        logger.debug(
            "Database config: host = %s, port = %s, database = %s, user = %s",
            db_config.host,
            db_config.port,
            db_config.database,
            db_config.username,
        )
        return db_config.url


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session generator for FastAPI dependency injection."""
    db: AsyncSession | None = None

    try:
        db = await DbSessionFactory.create_session()
        yield db
    except OperationalError as e:
        logger.error("Failed to connect to database: %s", e)
        logger.error(
            "Please ensure the database server is running and accessible."
        )
        raise
    except DatabaseError as e:
        logger.error("Database access error: %s", e)
        logger.error("Check database permissions and table accessibility.")
        raise
    except SQLAlchemyError as e:
        logger.error("Database session error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error getting DB session: %s", e)
        raise
    finally:
        if db is not None:
            try:
                await db.close()
                logger.debug(
                    "Database session closed successfully. "
                    "Session ID: %s", id(db)
                )
            except (SQLAlchemyError, OSError, IOError) as e:
                logger.warning("Error closing database session: %s", e)


async def get_db_session() -> AsyncSession:
    """Get an async database session for non-FastAPI usage."""
    try:
        db = await DbSessionFactory.create_session()
        logger.debug(
            "Database session created successfully. "
            "Session ID: %s", id(db)
        )
        return db
    except OperationalError as e:
        logger.error("Failed to connect to database: %s", e)
        logger.error(
            "Please ensure the database server is running and "
            "accessible."
        )
        raise
    except DatabaseError as e:
        logger.error("Database access error: %s", e)
        logger.error("Check database permissions and table accessibility.")
        raise
    except SQLAlchemyError as e:
        logger.error("Database session error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error getting DB session: %s", e)
        raise


def get_db_context():
    """Get an async database session context manager for safe
    session handling."""

    @asynccontextmanager
    async def db_context():
        db: AsyncSession | None = None
        try:
            db = await get_db_session()
            yield db
        except Exception as e:
            if db:
                await db.rollback()
            logger.error("Error in DB context: %s", e)
            raise
        finally:
            if db:
                try:
                    await db.close()
                    logger.debug(
                        "Database session closed successfully. "
                        "Session ID: %s", id(db)
                    )
                except (SQLAlchemyError, OSError, IOError) as e:
                    logger.warning("Error closing database session: %s", e)

    return db_context()

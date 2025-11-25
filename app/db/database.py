from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Optimize connection pool for Render/Neon
# Detect environment: use NullPool for Render/production by default
environment = os.getenv("ENVIRONMENT", "development")
is_render = "RENDER" in os.environ or "onrender.com" in os.getenv("DATABASE_URL", "")

logger.info(f"🔧 Environment: {environment}, Is Render: {is_render}")

# Use NullPool for Render/production, QueuePool for local development
if is_render or environment == "production":
    # Production/Render: Use NullPool to avoid connection pooling issues
    # Neon handles connection management, we just create fresh connections
    logger.info("🔧 Using NullPool for Render/production (Neon serverless)")
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
        }
    )
else:
    # Local development: Use QueuePool with optimized settings
    logger.info("🔧 Using QueuePool for local development")
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,    # Recycle connections every hour
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
        }
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

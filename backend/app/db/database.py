from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine with proper connection pool settings for Neon
# Note: Neon URLs already include sslmode=require, so we don't need to pass ssl
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connection before using it (important for Neon)
    pool_recycle=3600,   # Recycle connections every hour
    pool_size=5,         # Connection pool size
    max_overflow=10,     # Max additional connections
    echo_pool=False,     # Set to True for debugging connection pool issues
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

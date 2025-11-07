# ============================================
# DATABASE CONNECTION - SQLAlchemy + psycopg3
# ============================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ IMPORTANTE: Cambiar el driver a psycopg
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Render compatible
    echo=True if os.getenv("ENV") == "development" else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
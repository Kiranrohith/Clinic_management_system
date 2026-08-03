import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from engine.config import settings

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = None
SessionLocal = None

def get_database_url():
    return settings.DATABASE_URL
def init_db_connection():
    global engine, SessionLocal
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)   
    logger.info("Database connected successfully")
def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database is not initialized. Call init_db_connection() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
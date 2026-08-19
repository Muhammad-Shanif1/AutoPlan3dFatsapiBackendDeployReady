from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from services.settings import settings

engine = create_engine(
    settings.DB_CONNECTION,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

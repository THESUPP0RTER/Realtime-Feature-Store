import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel
from tenacity import retry, stop_after_attempt, wait_fixed

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(1),
)
def init_db():
   SQLModel.metadata.create_all(engine)

def get_session_context():
    """Generator function that yields a database session and closes it after use"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
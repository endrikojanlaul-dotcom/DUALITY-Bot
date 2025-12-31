import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import config


DATABASE_URL = os.getenv('DATABASE_URL', config.DATABASE_URL)

# Use a synchronous engine; DB calls run in executor when used from async code
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def init_db():
    # Import models to register
    from . import models
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()

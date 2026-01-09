import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# SQLAlchemy Base for models
Base = declarative_base()
logger = logging.getLogger("db")


def get_database_url() -> str:
	url = os.getenv("DATABASE_URL")
	if not url:
		raise RuntimeError(
			"DATABASE_URL environment variable is not set. Example: postgresql+psycopg2://user:pass@localhost:5432/stacktracker"
		)
	return url


DATABASE_URL = get_database_url()

# Create engine and session factory
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
	# Needed for FastAPI's TestClient (threaded) and SQLite
	connect_args = {"check_same_thread": False}

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	future=True,
	connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


async def init_db() -> None:
	# Import models to register them with Base.metadata
	from ..models import user  # noqa: F401
	logger.info("Initializing database and creating tables if absent")
	Base.metadata.create_all(bind=engine)


async def dispose_engine() -> None:
	# Dispose connections cleanly on shutdown
	logger.info("Disposing DB engine")
	engine.dispose()


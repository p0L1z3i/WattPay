"""This module initializes the SQLAlchemy Base and imports all ORM models."""
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

Base = declarative_base(metadata=MetaData(schema="SaiKrupa"))

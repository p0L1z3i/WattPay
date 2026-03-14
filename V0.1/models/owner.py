"""
Owner ORM Model
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    MetaData,
    DateTime,
)
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import declarative_base

Base = declarative_base(metadata=MetaData(schema="SaiKrupa"))


class Owner(Base):
    "Owner Database Model"
    __tablename__ = "owners"

    owner_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    owner_name = Column(String(100), nullable=False)
    owner_contact = Column(String(15), nullable=False)
    owner_created_at = Column(
        DateTime(timezone=False),
        server_default=now()
    )
    owner_updated_at = Column(
        DateTime(timezone=False),
        onupdate=now()
    )

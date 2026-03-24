"""
Owner ORM Model
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import relationship

from models import Base


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
        nullable=False,
        server_default=now()
    )
    owner_updated_at = Column(
        DateTime(timezone=False),
        nullable=True,
        onupdate=now()
    )

    tenant = relationship("Tenant", back_populates="owner")

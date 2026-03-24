"""
Tenant ORM Model
"""
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import relationship

from models import Base


class Tenant(Base):
    "Tenant Database Model"
    __tablename__ = "tenants"

    tenant_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    tenant_owner = Column(
        Integer,
        ForeignKey(
            "SaiKrupa.owners.owner_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )
    tenant_name = Column(String(100), nullable=False)
    tenant_contact = Column(String(15), nullable=False)
    tenant_created_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=now()
    )
    tenant_updated_at = Column(
        DateTime(timezone=False),
        nullable=True,
        onupdate=now()
    )

    owner = relationship("Owner", back_populates="tenant")

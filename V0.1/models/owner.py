"""
Owner ORM Model
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    MetaData,
    DateTime,
)
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import relationship, declarative_base

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
    owner_email = Column(String(200), unique=True, server_default="NA")
    owner_status = Column(String(20))
    owner_created_at = Column(
        DateTime(timezone=True),
        server_default=now()
    )
    owner_updated_at = Column(
        DateTime(timezone=True),
        onupdate=now()
    )

    # Relationship to Property
    properties = relationship(
        "Property",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Property(Base):
    "Property Database Model"
    __tablename__ = "properties"

    property_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(
        Integer,
        ForeignKey(
            "owners.owner_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )
    property_name = Column(String(150))
    property_locality = Column(String(100), nullable=False)
    property_city = Column(String(100), nullable=False)
    property_type = Column(String(20))
    property_created_at = Column(
        DateTime(timezone=True),
        server_default=now()
    )

    # Relationships
    owner = relationship("Owner", back_populates="properties")
    units = relationship(
        "Unit",
        back_populates="property",
        cascade="all, delete-orphan"
    )


class Unit(Base):
    "Unit Database Model"
    __tablename__ = "unit"

    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(
        Integer,
        ForeignKey(
            "properties.property_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    unit_number = Column(Text, nullable=False)
    floor = Column(String(1), nullable=False)
    unit_type = Column(Text, nullable=False)
    status = Column(Text)
    unit_created_at = Column(
        DateTime(timezone=True),
        server_default=now()
    )

    # Relationships
    property = relationship("Property", back_populates="units")

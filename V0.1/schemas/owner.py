"""
Pydantic Schemas For Owner
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer, field_validator


class OwnerBase(BaseModel):
    "owner base model(shared fields)"

    owner_name: str
    owner_contact: str
    owner_email: Optional[str] = "NA"
    owner_status: str


class OwnerCreate(OwnerBase):
    "Schema for creating an owner (input)"
    owner_created_at: Optional[datetime] = None

    @field_validator("owner_created_at", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        "Treat empty string as None"
        if value == "":
            return None
        return value


class OwnerUpdate(OwnerBase):
    "Schema for updating an owner (input)"
    owner_updated_at: Optional[datetime] = None

    @field_validator("owner_updated_at", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        "Treat empty string as None"
        if value == "":
            return None
        return value


class OwnerResponse(OwnerBase):
    "Schema for owner response (output)"

    owner_id: int
    owner_created_at: datetime
    owner_updated_at: Optional[datetime] = None

    @field_serializer("owner_created_at", "owner_updated_at")
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        "Format datetime fields to YYYY-MM-DD HH:MM:SS"
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None

    class Config:
        "allows ORM objects to be converted directly to JSON"
        from_attributes = True

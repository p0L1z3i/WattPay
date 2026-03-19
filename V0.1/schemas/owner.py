"""
Pydantic Schemas For Owner
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OwnerBase(BaseModel):
    "owner base model(shared fields)"

    owner_name: str
    owner_contact: str


class OwnerCreate(OwnerBase):
    "Schema for creating an owner (input)"


class OwnerUpdate(OwnerBase):
    "Schema for updating an owner (input)"


class OwnerResponse(OwnerBase):
    "Schema for owner response (output)"

    owner_id: int
    owner_name: str
    owner_contact: str
    owner_created_at: Optional[datetime] = None
    owner_updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")},
    )

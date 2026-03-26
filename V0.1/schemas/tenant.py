"""
Pydantic Schemas For Owner
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OwnerBase(BaseModel):
    "owner base model(shared fields)"

    tenant_name: str
    owner_contact: str


class OwnerCreate(OwnerBase):
    "Schema for creating an owner (input)"
    owner_created_at: Optional[datetime] = None


class OwnerUpdate(OwnerBase):
    "Schema for updating an owner (input)"
    owner_updated_at: Optional[datetime] = None


class OwnerResponse(OwnerBase):
    "Schema for owner response (output)"

    owner_id: int
    owner_created_at: datetime
    owner_updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

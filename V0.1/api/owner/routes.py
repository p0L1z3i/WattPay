"""
Docstring for api.owner.routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.db_session_maker import get_db
from api.common.log.logging import get_logger

from services import owner_service
from schemas.owner import OwnerCreate, OwnerResponse, OwnerUpdate

logger = get_logger(__name__)

router = APIRouter()


@router.get("/get-all-owners", response_model=List[OwnerResponse])
async def get_all_owners(db: AsyncSession = Depends(get_db)):
    "Get all owner details"

    logger.debug("GET /owner/get-all-owners called")
    result = await owner_service.get_all_owners(db)
    if not result:
        logger.warning("GET /owner/get-all-owners - no owners found")
        raise HTTPException(status_code=404, detail="No Owners Available")
    logger.debug(
        "GET /owner/get-all-owners - returning %d owner(s)", len(result)
    )
    return result


@router.get("/get-owner-by-name/{owner_name}", response_model=OwnerResponse)
async def get_owner_by_name(
    owner_name: str, db: AsyncSession = Depends(get_db)
):
    "Get owner details by name"

    logger.debug(
        "GET /owner/get-owner-by-name/%s called", owner_name
    )
    if not owner_name.strip():
        logger.warning(
            "GET /owner/get-owner-by-name - invalid owner_name provided"
        )
        raise HTTPException(status_code=400, detail="Invalid owner name")
    result = await owner_service.get_owner_by_name(db, owner_name)
    if not result:
        logger.warning(
            "GET /owner/get-owner-by-name/%s - owner not found",
            owner_name,
        )
        raise HTTPException(status_code=404, detail="Owner Not Found")
    logger.debug(
        "GET /owner/get-owner-by-name/%s - owner found with id: %d",
        owner_name,
        result.owner_id,
    )
    return result


@router.get(
    "/get-owner-by-contact/{owner_contact}",
    response_model=OwnerResponse,
)
async def get_owner_by_contact(
    owner_contact: str, db: AsyncSession = Depends(get_db)
):
    "Get owner details by contact"

    logger.debug(
        "GET /owner/get-owner-by-contact/%s called", owner_contact
    )
    if not owner_contact.strip():
        logger.warning(
            "GET /owner/get-owner-by-contact - invalid owner_contact provided"
        )
        raise HTTPException(status_code=400, detail="Invalid owner contact")
    result = await owner_service.get_owner_by_contact(db, owner_contact)
    if not result:
        logger.warning(
            "GET /owner/get-owner-by-contact/%s - owner not found",
            owner_contact,
        )
        raise HTTPException(status_code=404, detail="Owner Not Found")
    logger.debug(
        "GET /owner/get-owner-by-contact/%s - owner found with id: %d",
        owner_contact,
        result.owner_id,
    )
    return result


@router.post("/add-owner", response_model=OwnerResponse)
async def insert_new_owner(
    owner: OwnerCreate, db: AsyncSession = Depends(get_db)
):
    "Insert new owner details"

    logger.debug(
        "POST /owner/add-owner called for owner: %s", owner.owner_name
    )
    result = await owner_service.add_owner(db, owner)

    if not result:
        logger.error(
            "POST /owner/add-owner - failed to add owner: %s",
            owner.owner_name,
        )
        raise HTTPException(status_code=400, detail="Failed to add owner")
    logger.debug("POST /owner/add-owner - owner added successfully")
    return result


@router.put("/update-owner/{owner_id}", response_model=OwnerResponse)
async def update_owner(
    owner_id: int, owner: OwnerUpdate, db: AsyncSession = Depends(get_db)
):
    "Update existing owner details"

    logger.debug("PUT /owner/update-owner/%d called", owner_id)
    result = await owner_service.update_owner(db, owner_id, owner)

    if not result:
        logger.error(
            "PUT /owner/update-owner/%d - failed to update owner",
            owner_id,
        )
        raise HTTPException(status_code=404, detail="Failed to update owner")
    logger.debug(
        "PUT /owner/update-owner/%d - owner updated successfully",
        owner_id,
    )
    return result


@router.patch("/update-owner/{owner_id}", response_model=OwnerResponse)
async def update_owner_contact(
    owner_id: int, new_contact: str, db: AsyncSession = Depends(get_db)
):
    "Update existing owner details by contact"

    cleaned_contact = new_contact.strip()
    if not cleaned_contact:
        logger.warning(
            "PATCH /owner/update-owner/%d"
            " - attempted to update with empty contact",
            owner_id,
        )
        raise HTTPException(
            status_code=400,
            detail="New contact must not be empty or whitespace only"
        )
    logger.debug(
        "PATCH /owner/update-owner/%s called", cleaned_contact
    )
    result = await owner_service.update_owner_contact(
        owner_id, cleaned_contact, db
    )

    if not result:
        logger.error(
            "PATCH /owner/update-owner/%s - failed to update owner contact",
            cleaned_contact,
        )
        raise HTTPException(
            status_code=404,
            detail="Failed to update owner contact"
        )
    logger.debug(
        "PATCH /owner/update-owner/%s - owner contact updated successfully",
        cleaned_contact,
    )
    return result


@router.delete("/delete-owner/{owner_id}")
async def delete_owner(owner_id: int, db: AsyncSession = Depends(get_db)):
    "Delete owner details by id"

    logger.debug("DELETE /owner/delete-owner/%d called", owner_id)
    result = await owner_service.delete_owner(db, owner_id)

    if not result:
        logger.error(
            "DELETE /owner/delete-owner/%d - failed to delete owner",
            owner_id,
        )
        raise HTTPException(status_code=404, detail="Failed to delete owner")
    logger.debug(
        "DELETE /owner/delete-owner/%d - owner deleted successfully",
        owner_id,
    )
    return {"message": "Owner deleted successfully"}

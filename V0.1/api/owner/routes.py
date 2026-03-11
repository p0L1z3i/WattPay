"""
Docstring for api.owner.routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.db_session_maker import get_db
from api.common.log.logging import get_logger

from services import owner_service
from schemas.owner import OwnerCreate, OwnerResponse

logger = get_logger(__name__)

router = APIRouter()


@router.get("/get-all-owners", response_model=List[OwnerResponse])
async def get_all_owners(db: AsyncSession = Depends(get_db)):
    "Get all owner details"

    logger.info("GET /owner/get-all-owners called")
    result = await owner_service.get_all_owners(db)
    if not result:
        logger.warning("GET /owner/get-all-owners - no owners found")
        raise HTTPException(status_code=404, detail="No Owners Available")
    logger.info(
        "GET /owner/get-all-owners - returning %d owner(s)", len(result)
    )
    return result


@router.get("/get-owner-by-name/{owner_name}", response_model=OwnerResponse)
async def get_owner_by_name(
    owner_name: str, db: AsyncSession = Depends(get_db)
):
    "Get owner details by name"

    logger.info(
        "GET /owner/get-owner-by-name/%s called", owner_name
    )
    result = await owner_service.get_owner_by_name(db, owner_name)
    if not result:
        logger.warning(
            "GET /owner/get-owner-by-name/%s - owner not found",
            owner_name,
        )
        raise HTTPException(status_code=404, detail="Owner Not Found")
    logger.info(
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

    logger.info(
        "GET /owner/get-owner-by-contact/%s called", owner_contact
    )
    result = await owner_service.get_owner_by_contact(db, owner_contact)
    if not result:
        logger.warning(
            "GET /owner/get-owner-by-contact/%s - owner not found",
            owner_contact,
        )
        raise HTTPException(status_code=404, detail="Owner Not Found")
    logger.info(
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

    logger.info("POST /owner/add-owner called for owner: %s", owner.owner_name)
    result = await owner_service.add_owner(db, owner)

    if not result:
        logger.error(
            "POST /owner/add-owner - failed to add owner: %s",
            owner.owner_name,
        )
        raise HTTPException(status_code=400, detail="Failed to add owner")
    logger.info("POST /owner/add-owner - owner added successfully")
    return result


@router.put("/update-owner/{owner_id}", response_model=OwnerResponse)
async def update_owner(
    owner_id: int, owner: OwnerCreate, db: AsyncSession = Depends(get_db)
):
    "Update existing owner details"

    logger.info("PUT /owner/update-owner/%d called", owner_id)
    result = await owner_service.update_owner(db, owner_id, owner)

    if not result:
        logger.error(
            "PUT /owner/update-owner/%d - failed to update owner",
            owner_id,
        )
        raise HTTPException(status_code=400, detail="Failed to update owner")
    logger.info(
        "PUT /owner/update-owner/%d - owner updated successfully",
        owner_id,
    )
    return result


@router.patch("/update-owner/{owner_id}", response_model=OwnerResponse)
async def update_owner_contact(
    owner_id: int, new_contact: str, db: AsyncSession = Depends(get_db)
):
    "Update existing owner details by contact"

    logger.info(
        "PATCH /owner/update-owner/%s called", new_contact
    )
    result = await owner_service.update_owner_contact(
        owner_id, new_contact, db
    )

    if not result:
        logger.error(
            "PATCH /owner/update-owner/%s - failed to update owner contact",
            new_contact,
        )
        raise HTTPException(
            status_code=400,
            detail="Failed to update owner contact"
        )
    logger.info(
        "PATCH /owner/update-owner/%s - owner contact updated successfully",
        new_contact,
    )
    return result

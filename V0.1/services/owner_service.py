"""
Docstring for services.owner_service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.owner import OwnerCreate, OwnerResponse
from models.owner import Owner
from api.common.log.logging import get_logger

logger = get_logger(__name__)


async def get_all_owners(
        db: AsyncSession
) -> list[OwnerResponse] | None:
    """Get All owners"""

    logger.debug("Fetching all owners")
    result = await db.execute(select(Owner))
    db_owner = result.scalars().all()

    if db_owner:
        logger.debug("Found %d owner(s)", len(db_owner))
        return [OwnerResponse.model_validate(o) for o in db_owner]

    logger.warning("No owners found")
    return None


async def get_owner_by_name(
        db: AsyncSession, owner_name: str
) -> OwnerResponse | None:
    """Get owner by name"""

    logger.debug("Fetching owner by name: %s", owner_name)
    result = await db.execute(
        select(Owner).where(Owner.owner_name == owner_name)
    )
    db_owner = result.scalars().first()

    if db_owner:
        logger.debug("Found owner with id: %d", db_owner.owner_id)
        return OwnerResponse.model_validate(db_owner)

    logger.warning("Owner not found with name: %s", owner_name)
    return None


async def get_owner_by_contact(
        db: AsyncSession, owner_contact: str
) -> OwnerResponse | None:
    """Get owner by contact"""

    logger.debug("Fetching owner by contact: %s", owner_contact)
    result = await db.execute(
        select(Owner).where(Owner.owner_contact == owner_contact)
    )
    db_owner = result.scalars().first()

    if db_owner:
        logger.debug("Found owner with id: %d", db_owner.owner_id)
        return OwnerResponse.model_validate(db_owner)

    logger.warning("Owner not found with contact: %s", owner_contact)
    return None


async def add_owner(
        db: AsyncSession, owner: OwnerCreate
) -> OwnerResponse | None:
    """Add new owner"""

    logger.debug("Adding new owner: %s", owner.owner_name)
    owner_data = {
        "owner_name": owner.owner_name,
        "owner_contact": owner.owner_contact,
        "owner_email": owner.owner_email,
        "owner_status": owner.owner_status,
    }
    if owner.owner_created_at is not None:
        owner_data["owner_created_at"] = owner.owner_created_at

    new_owner = Owner(**owner_data)
    db.add(new_owner)
    await db.commit()
    await db.refresh(new_owner)

    if new_owner:
        logger.debug(
            "Owner added successfully with id: %s", new_owner.owner_id
        )
        return OwnerResponse.model_validate(new_owner)

    logger.error("Failed to add owner: %s", owner.owner_name)
    return None

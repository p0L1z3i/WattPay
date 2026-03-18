"""
Docstring for services.owner_service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse
from models.owner import Owner
from api.common.log.logging import get_logger

logger = get_logger(__name__)


async def get_all_owners(
        db: AsyncSession
) -> list[OwnerResponse]:
    """Get All owners"""

    logger.info("Fetching all owners")
    db_owner = (await db.scalars(select(Owner))).all()

    if db_owner:
        logger.info("Found %d owner(s)", len(db_owner))
        return [OwnerResponse.model_validate(o) for o in db_owner]

    logger.warning("No owners found")
    return []


async def get_owner_by_name(
        db: AsyncSession, owner_name: str
) -> OwnerResponse | None:
    """Get owner by name"""

    logger.info("Fetching owner by name: %s", owner_name)
    result = await db.execute(
        select(Owner).where(Owner.owner_name == owner_name)
    )
    db_owner = result.scalars().first()

    if db_owner:
        logger.info("Found owner with id: %d", db_owner.owner_id)
        return OwnerResponse.model_validate(db_owner)

    logger.warning("Owner not found with name: %s", owner_name)
    return None


async def get_owner_by_contact(
        db: AsyncSession, owner_contact: str
) -> OwnerResponse | None:
    """Get owner by contact"""

    logger.info("Fetching owner by contact: %s", owner_contact)
    result = await db.execute(
        select(Owner).where(Owner.owner_contact == owner_contact)
    )
    db_owner = result.scalars().first()

    if db_owner:
        logger.info("Found owner with id: %d", db_owner.owner_id)
        return OwnerResponse.model_validate(db_owner)

    logger.warning("Owner not found with contact: %s", owner_contact)
    return None


async def add_owner(
        db: AsyncSession, owner: OwnerCreate
) -> OwnerResponse | None:
    """Add new owner"""

    logger.info("Adding new owner: %s", owner.owner_name)
    owner_data = {
        "owner_name": owner.owner_name,
        "owner_contact": owner.owner_contact,
    }
    if owner.owner_created_at is not None:
        owner_data["owner_created_at"] = owner.owner_created_at

    new_owner = Owner(**owner_data)

    try:
        db.add(new_owner)
        await db.commit()
        await db.refresh(new_owner)
    except Exception as e:
        logger.error(
            "Error adding owner: %s, error: %s", owner.owner_name, str(e)
        )
        await db.rollback()
        return None

    logger.info(
        "Owner added successfully with id: %s", new_owner.owner_id
    )
    return OwnerResponse.model_validate(new_owner)


async def update_owner(
        db: AsyncSession, owner_id: int, owner: OwnerUpdate
) -> OwnerResponse | None:
    """Update owner details"""

    logger.info("Updating owner with id: %d", owner_id)

    db_owner = await db.get(Owner, owner_id)

    if not db_owner:
        logger.warning("Owner not found with id: %d", owner_id)
        return None

    db_owner.owner_name = owner.owner_name
    db_owner.owner_contact = owner.owner_contact
    if owner.owner_updated_at is not None:
        db_owner.owner_updated_at = owner.owner_updated_at

    await db.commit()
    await db.refresh(db_owner)

    logger.info("Owner updated successfully with id: %d", owner_id)
    return OwnerResponse.model_validate(db_owner)


async def update_owner_contact(
        owner_id: int, new_contact: str, db: AsyncSession
) -> OwnerResponse | None:
    """Update contact number for owner"""

    logger.info(
        "Updating contact for owner with id: %d to new contact: %s",
        owner_id,
        new_contact,
    )

    db_owner = await db.get(Owner, owner_id)

    if not db_owner:
        logger.warning("Owner not found with id: %d", owner_id)
        return None

    db_owner.owner_contact = new_contact
    await db.commit()
    await db.refresh(db_owner)

    logger.info(
        "Owner contact updated successfully for id: %d", owner_id
    )
    return OwnerResponse.model_validate(db_owner)


async def delete_owner(
        db: AsyncSession, owner_id: int
) -> bool:
    """Delete owner by id"""

    logger.info("Deleting owner with id: %d", owner_id)

    db_owner = await db.get(Owner, owner_id)

    if not db_owner:
        logger.warning("Owner not found with id: %d", owner_id)
        return False

    await db.delete(db_owner)
    await db.commit()

    logger.info("Owner deleted successfully with id: %d", owner_id)
    return True

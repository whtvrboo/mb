"""Assets module service layer. PRIVATE - other modules import from interface.py."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError
from mitlist.modules.assets.models import (
    AssetInsurance,
    HomeAsset,
    MaintenanceLog,
    MaintenanceTask,
)


# ---------- Assets ----------
async def list_assets(db: AsyncSession, group_id: int) -> list[HomeAsset]:
    """List assets in a group."""
    result = await db.execute(
        select(HomeAsset).where(HomeAsset.group_id == group_id).order_by(HomeAsset.name)
    )
    return list(result.scalars().all())


async def get_asset(db: AsyncSession, asset_id: int) -> HomeAsset | None:
    """Get asset by ID."""
    result = await db.execute(select(HomeAsset).where(HomeAsset.id == asset_id))
    return result.scalar_one_or_none()


async def create_asset(
    db: AsyncSession,
    group_id: int,
    name: str,
    asset_type: str,
    location_id: int | None = None,
    brand: str | None = None,
    model_number: str | None = None,
    serial_number: str | None = None,
    purchase_date: datetime | None = None,
    purchase_price: float | None = None,
    purchase_store: str | None = None,
    warranty_end_date: datetime | None = None,
    warranty_type: str | None = None,
    energy_rating: str | None = None,
    photo_url: str | None = None,
    manual_document_id: int | None = None,
    receipt_document_id: int | None = None,
    service_contact_id: int | None = None,
) -> HomeAsset:
    """Create a new asset."""
    asset = HomeAsset(
        group_id=group_id,
        name=name,
        asset_type=asset_type,
        location_id=location_id,
        brand=brand,
        model_number=model_number,
        serial_number=serial_number,
        purchase_date=purchase_date,
        purchase_price=purchase_price,
        purchase_store=purchase_store,
        warranty_end_date=warranty_end_date,
        warranty_type=warranty_type,
        energy_rating=energy_rating,
        photo_url=photo_url,
        manual_document_id=manual_document_id,
        receipt_document_id=receipt_document_id,
        service_contact_id=service_contact_id,
        is_active=True,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return asset


async def update_asset(
    db: AsyncSession,
    asset_id: int,
    name: str | None = None,
    asset_type: str | None = None,
    location_id: int | None = None,
    brand: str | None = None,
    model_number: str | None = None,
    serial_number: str | None = None,
    purchase_date: datetime | None = None,
    purchase_price: float | None = None,
    purchase_store: str | None = None,
    warranty_end_date: datetime | None = None,
    warranty_type: str | None = None,
    energy_rating: str | None = None,
    photo_url: str | None = None,
    manual_document_id: int | None = None,
    receipt_document_id: int | None = None,
    service_contact_id: int | None = None,
    is_active: bool | None = None,
) -> HomeAsset:
    """Update asset details."""
    asset = await get_asset(db, asset_id)
    if not asset:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    if name is not None:
        asset.name = name
    if asset_type is not None:
        asset.asset_type = asset_type
    if location_id is not None:
        asset.location_id = location_id
    if brand is not None:
        asset.brand = brand
    if model_number is not None:
        asset.model_number = model_number
    if serial_number is not None:
        asset.serial_number = serial_number
    if purchase_date is not None:
        asset.purchase_date = purchase_date
    if purchase_price is not None:
        asset.purchase_price = purchase_price
    if purchase_store is not None:
        asset.purchase_store = purchase_store
    if warranty_end_date is not None:
        asset.warranty_end_date = warranty_end_date
    if warranty_type is not None:
        asset.warranty_type = warranty_type
    if energy_rating is not None:
        asset.energy_rating = energy_rating
    if photo_url is not None:
        asset.photo_url = photo_url
    if manual_document_id is not None:
        asset.manual_document_id = manual_document_id
    if receipt_document_id is not None:
        asset.receipt_document_id = receipt_document_id
    if service_contact_id is not None:
        asset.service_contact_id = service_contact_id
    if is_active is not None:
        asset.is_active = is_active

    await db.flush()
    await db.refresh(asset)
    return asset


async def dispose_asset(
    db: AsyncSession,
    asset_id: int,
    disposed_at: datetime,
) -> HomeAsset:
    """Mark asset as disposed."""
    asset = await get_asset(db, asset_id)
    if not asset:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    asset.is_active = False
    asset.disposed_at = disposed_at

    await db.flush()
    await db.refresh(asset)
    return asset


# ---------- Maintenance Tasks ----------
async def get_maintenance_task(db: AsyncSession, task_id: int) -> MaintenanceTask | None:
    """Get maintenance task by ID with asset loaded (for group ownership check)."""
    result = await db.execute(
        select(MaintenanceTask)
        .where(MaintenanceTask.id == task_id)
        .options(selectinload(MaintenanceTask.asset))
    )
    return result.scalar_one_or_none()


async def list_maintenance_tasks(db: AsyncSession, asset_id: int) -> list[MaintenanceTask]:
    """List maintenance tasks for an asset."""
    result = await db.execute(select(MaintenanceTask).where(MaintenanceTask.asset_id == asset_id))
    return list(result.scalars().all())


async def create_maintenance_task(
    db: AsyncSession,
    asset_id: int,
    name: str,
    frequency_days: int,
    priority: str | None = None,
    instructions: str | None = None,
    estimated_duration_minutes: int | None = None,
    estimated_cost: float | None = None,
    required_item_concept_id: int | None = None,
) -> MaintenanceTask:
    """Create a maintenance task."""
    asset = await get_asset(db, asset_id)
    if not asset:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    task = MaintenanceTask(
        asset_id=asset_id,
        name=name,
        frequency_days=frequency_days,
        priority=priority,
        instructions=instructions,
        estimated_duration_minutes=estimated_duration_minutes,
        estimated_cost=estimated_cost,
        required_item_concept_id=required_item_concept_id,
        is_active=True,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def update_maintenance_task(
    db: AsyncSession,
    task_id: int,
    name: str | None = None,
    frequency_days: int | None = None,
    priority: str | None = None,
    instructions: str | None = None,
    estimated_duration_minutes: int | None = None,
    estimated_cost: float | None = None,
    required_item_concept_id: int | None = None,
    is_active: bool | None = None,
) -> MaintenanceTask:
    """Update maintenance task."""
    result = await db.execute(select(MaintenanceTask).where(MaintenanceTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundError(code="TASK_NOT_FOUND", detail=f"Task {task_id} not found")

    if name is not None:
        task.name = name
    if frequency_days is not None:
        task.frequency_days = frequency_days
    if priority is not None:
        task.priority = priority
    if instructions is not None:
        task.instructions = instructions
    if estimated_duration_minutes is not None:
        task.estimated_duration_minutes = estimated_duration_minutes
    if estimated_cost is not None:
        task.estimated_cost = estimated_cost
    if required_item_concept_id is not None:
        task.required_item_concept_id = required_item_concept_id
    if is_active is not None:
        task.is_active = is_active

    await db.flush()
    await db.refresh(task)
    return task


# ---------- Maintenance Logs ----------
async def list_maintenance_logs(db: AsyncSession, task_id: int) -> list[MaintenanceLog]:
    """List logs for a task."""
    result = await db.execute(
        select(MaintenanceLog)
        .where(MaintenanceLog.task_id == task_id)
        .order_by(MaintenanceLog.completed_at.desc())
    )
    return list(result.scalars().all())


async def create_maintenance_log(
    db: AsyncSession,
    task_id: int,
    user_id: int,
    completed_at: datetime,
    actual_duration_minutes: int | None = None,
    notes: str | None = None,
    photo_url: str | None = None,
    quality_rating: int | None = None,
    cost_expense_id: int | None = None,
) -> MaintenanceLog:
    """Log completed maintenance."""
    # Fetch task to verify
    result = await db.execute(select(MaintenanceTask).where(MaintenanceTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundError(code="TASK_NOT_FOUND", detail=f"Task {task_id} not found")

    log = MaintenanceLog(
        task_id=task_id,
        user_id=user_id,
        completed_at=completed_at,
        actual_duration_minutes=actual_duration_minutes,
        notes=notes,
        photo_url=photo_url,
        quality_rating=quality_rating,
        cost_expense_id=cost_expense_id,
    )
    db.add(log)

    # Update task details (last completed and next due)
    task.last_completed_at = completed_at
    if task.frequency_days:
        task.next_due_date = completed_at + timedelta(days=task.frequency_days)

    await db.flush()
    await db.refresh(log)
    await db.refresh(task)
    return log


# ---------- Insurance ----------
async def get_insurance_by_id(db: AsyncSession, insurance_id: int) -> AssetInsurance | None:
    """Get insurance by ID (for group ownership check)."""
    result = await db.execute(select(AssetInsurance).where(AssetInsurance.id == insurance_id))
    return result.scalar_one_or_none()


async def list_insurances(db: AsyncSession, group_id: int) -> list[AssetInsurance]:
    """List insurance policies."""
    result = await db.execute(select(AssetInsurance).where(AssetInsurance.group_id == group_id))
    return list(result.scalars().all())


async def create_insurance(
    db: AsyncSession,
    group_id: int,
    policy_number: str,
    provider_name: str,
    coverage_type: str,
    premium_amount: float,
    premium_frequency: str,
    start_date: datetime,
    end_date: datetime | None = None,
    deductible_amount: float | None = None,
    document_id: int | None = None,
) -> AssetInsurance:
    """Create insurance policy."""
    ins = AssetInsurance(
        group_id=group_id,
        policy_number=policy_number,
        provider_name=provider_name,
        coverage_type=coverage_type,
        premium_amount=premium_amount,
        premium_frequency=premium_frequency,
        start_date=start_date,
        end_date=end_date,
        deductible_amount=deductible_amount,
        document_id=document_id,
    )
    db.add(ins)
    await db.flush()
    await db.refresh(ins)
    return ins


async def update_insurance(
    db: AsyncSession,
    insurance_id: int,
    policy_number: str | None = None,
    provider_name: str | None = None,
    coverage_type: str | None = None,
    premium_amount: float | None = None,
    premium_frequency: str | None = None,
    end_date: datetime | None = None,
    deductible_amount: float | None = None,
    document_id: int | None = None,
) -> AssetInsurance:
    """Update insurance policy."""
    result = await db.execute(select(AssetInsurance).where(AssetInsurance.id == insurance_id))
    ins = result.scalar_one_or_none()
    if not ins:
        raise NotFoundError(
            code="INSURANCE_NOT_FOUND", detail=f"Insurance {insurance_id} not found"
        )

    if policy_number is not None:
        ins.policy_number = policy_number
    if provider_name is not None:
        ins.provider_name = provider_name
    if coverage_type is not None:
        ins.coverage_type = coverage_type
    if premium_amount is not None:
        ins.premium_amount = premium_amount
    if premium_frequency is not None:
        ins.premium_frequency = premium_frequency
    if end_date is not None:
        ins.end_date = end_date
    if deductible_amount is not None:
        ins.deductible_amount = deductible_amount
    if document_id is not None:
        ins.document_id = document_id

    await db.flush()
    await db.refresh(ins)
    return ins

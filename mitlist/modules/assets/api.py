"""Assets module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_db, get_current_group_id, get_current_user
from mitlist.core.errors import NotFoundError, ValidationError
from mitlist.modules.assets import interface, schemas

router = APIRouter(prefix="/assets", tags=["assets"])


# ---------- Assets ----------
@router.get("", response_model=ListType[schemas.HomeAssetResponse])
async def get_assets(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List assets in the group."""
    assets = await interface.list_assets(db, group_id)
    return [schemas.HomeAssetResponse.model_validate(a) for a in assets]


@router.post("", response_model=schemas.HomeAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    data: schemas.HomeAssetCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new asset."""
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id mismatch")

    asset = await interface.create_asset(
        db,
        group_id=group_id,
        name=data.name,
        asset_type=data.asset_type,
        location_id=data.location_id,
        brand=data.brand,
        model_number=data.model_number,
        serial_number=data.serial_number,
        purchase_date=data.purchase_date,
        purchase_price=data.purchase_price,
        purchase_store=data.purchase_store,
        warranty_end_date=data.warranty_end_date,
        warranty_type=data.warranty_type,
        energy_rating=data.energy_rating,
        photo_url=data.photo_url,
        manual_document_id=data.manual_document_id,
        receipt_document_id=data.receipt_document_id,
        service_contact_id=data.service_contact_id,
    )
    return schemas.HomeAssetResponse.model_validate(asset)


@router.get("/{asset_id}", response_model=schemas.HomeAssetResponse)
async def get_asset(
    asset_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get asset details."""
    asset = await interface.get_asset(db, asset_id)
    if not asset or asset.group_id != group_id:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")
    return schemas.HomeAssetResponse.model_validate(asset)


@router.patch("/{asset_id}", response_model=schemas.HomeAssetResponse)
async def update_asset(
    asset_id: int,
    data: schemas.HomeAssetUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Update asset details."""
    asset = await interface.get_asset(db, asset_id)
    if not asset or asset.group_id != group_id:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    updated = await interface.update_asset(
        db,
        asset_id=asset_id,
        name=data.name,
        asset_type=data.asset_type,
        location_id=data.location_id,
        brand=data.brand,
        model_number=data.model_number,
        serial_number=data.serial_number,
        purchase_date=data.purchase_date,
        purchase_price=data.purchase_price,
        purchase_store=data.purchase_store,
        warranty_end_date=data.warranty_end_date,
        warranty_type=data.warranty_type,
        energy_rating=data.energy_rating,
        photo_url=data.photo_url,
        manual_document_id=data.manual_document_id,
        receipt_document_id=data.receipt_document_id,
        service_contact_id=data.service_contact_id,
        is_active=data.is_active,
    )
    return schemas.HomeAssetResponse.model_validate(updated)


@router.post("/{asset_id}/dispose", response_model=schemas.HomeAssetResponse)
async def dispose_asset(
    asset_id: int,
    data: schemas.HomeAssetDisposeRequest,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Mark asset as disposed."""
    asset = await interface.get_asset(db, asset_id)
    if not asset or asset.group_id != group_id:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    updated = await interface.dispose_asset(db, asset_id, data.disposed_at)
    return schemas.HomeAssetResponse.model_validate(updated)


# ---------- Maintenance Tasks ----------
@router.get("/{asset_id}/tasks", response_model=ListType[schemas.MaintenanceTaskResponse])
async def get_maintenance_tasks(
    asset_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get maintenance tasks."""
    asset = await interface.get_asset(db, asset_id)
    if not asset or asset.group_id != group_id:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")

    tasks = await interface.list_maintenance_tasks(db, asset_id)
    return [schemas.MaintenanceTaskResponse.model_validate(t) for t in tasks]


@router.post("/{asset_id}/tasks", response_model=schemas.MaintenanceTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_task(
    asset_id: int,
    data: schemas.MaintenanceTaskCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a maintenance task."""
    asset = await interface.get_asset(db, asset_id)
    if not asset or asset.group_id != group_id:
        raise NotFoundError(code="ASSET_NOT_FOUND", detail=f"Asset {asset_id} not found")
        
    if data.asset_id != asset_id:
        raise ValidationError(code="ID_MISMATCH", detail="Body asset_id must match path")

    task = await interface.create_maintenance_task(
        db,
        asset_id=asset_id,
        name=data.name,
        frequency_days=data.frequency_days,
        priority=data.priority,
        instructions=data.instructions,
        estimated_duration_minutes=data.estimated_duration_minutes,
        estimated_cost=data.estimated_cost,
        required_item_concept_id=data.required_item_concept_id,
    )
    return schemas.MaintenanceTaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=schemas.MaintenanceTaskResponse)
async def update_maintenance_task(
    task_id: int,
    data: schemas.MaintenanceTaskUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Update maintenance task."""
    task = await interface.get_maintenance_task(db, task_id)
    if not task or task.asset.group_id != group_id:
        raise NotFoundError(code="TASK_NOT_FOUND", detail=f"Task {task_id} not found")
    updated = await interface.update_maintenance_task(
        db,
        task_id=task_id,
        name=data.name,
        frequency_days=data.frequency_days,
        priority=data.priority,
        instructions=data.instructions,
        estimated_duration_minutes=data.estimated_duration_minutes,
        estimated_cost=data.estimated_cost,
        required_item_concept_id=data.required_item_concept_id,
        is_active=data.is_active,
    )
    return schemas.MaintenanceTaskResponse.model_validate(updated)


# ---------- Maintenance Logs ----------
@router.get("/tasks/{task_id}/logs", response_model=ListType[schemas.MaintenanceLogResponse])
async def get_maintenance_logs(
    task_id: int,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Get maintenance logs."""
    task = await interface.get_maintenance_task(db, task_id)
    if not task or task.asset.group_id != group_id:
        raise NotFoundError(code="TASK_NOT_FOUND", detail=f"Task {task_id} not found")
    logs = await interface.list_maintenance_logs(db, task_id)
    return [schemas.MaintenanceLogResponse.model_validate(l) for l in logs]


@router.post("/tasks/{task_id}/logs", response_model=schemas.MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_log(
    task_id: int,
    data: schemas.MaintenanceCompleteRequest,
    group_id: int = Depends(get_current_group_id),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log completed maintenance."""
    task = await interface.get_maintenance_task(db, task_id)
    if not task or task.asset.group_id != group_id:
        raise NotFoundError(code="TASK_NOT_FOUND", detail=f"Task {task_id} not found")
    log = await interface.create_maintenance_log(
        db,
        task_id=task_id,
        user_id=user.id,
        completed_at=data.disposed_at if hasattr(data, 'disposed_at') else datetime.utcnow(), # Wait, request schema doesn't have completed_at?
        # Check schemas.MaintenanceCompleteRequest (Step 173).
        # It has actual_duration_minutes, notes, photo_url, quality_rating, cost_expense_id.
        # It misses "completed_at".
        # I'll assume "now" if missing, or use default from model.
        # Service expects completed_at.
        
        actual_duration_minutes=data.actual_duration_minutes,
        notes=data.notes,
        photo_url=data.photo_url,
        quality_rating=data.quality_rating,
        cost_expense_id=data.cost_expense_id,
    )
    return schemas.MaintenanceLogResponse.model_validate(log)

# CORRECTION: datetime import needed inside function if used? I imported it at top level but need to check if user passed it.
from datetime import datetime
# Re-check MaintenanceCompleteRequest.
# It does NOT have completed_at. So I use current time.

# ---------- Insurance ----------
@router.get("/insurance", response_model=ListType[schemas.AssetInsuranceResponse])
async def get_insurances(
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """List insurances."""
    insurances = await interface.list_insurances(db, group_id)
    return [schemas.AssetInsuranceResponse.model_validate(i) for i in insurances]


@router.post("/insurance", response_model=schemas.AssetInsuranceResponse, status_code=status.HTTP_201_CREATED)
async def create_insurance(
    data: schemas.AssetInsuranceCreate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Create insurance policy."""
    if data.group_id != group_id:
        raise ValidationError(code="GROUP_MISMATCH", detail="group_id mismatch")

    ins = await interface.create_insurance(
        db,
        group_id=group_id,
        policy_number=data.policy_number,
        provider_name=data.provider_name,
        coverage_type=data.coverage_type,
        premium_amount=data.premium_amount,
        premium_frequency=data.premium_frequency,
        start_date=data.start_date,
        end_date=data.end_date,
        deductible_amount=data.deductible_amount,
        document_id=data.document_id,
    )
    return schemas.AssetInsuranceResponse.model_validate(ins)


@router.patch("/insurance/{insurance_id}", response_model=schemas.AssetInsuranceResponse)
async def update_insurance(
    insurance_id: int,
    data: schemas.AssetInsuranceUpdate,
    group_id: int = Depends(get_current_group_id),
    db: AsyncSession = Depends(get_db),
):
    """Update insurance policy."""
    ins = await interface.get_insurance_by_id(db, insurance_id)
    if not ins or ins.group_id != group_id:
        raise NotFoundError(code="INSURANCE_NOT_FOUND", detail=f"Insurance {insurance_id} not found")
    updated = await interface.update_insurance(
        db,
        insurance_id=insurance_id,
        policy_number=data.policy_number,
        provider_name=data.provider_name,
        coverage_type=data.coverage_type,
        premium_amount=data.premium_amount,
        premium_frequency=data.premium_frequency,
        end_date=data.end_date,
        deductible_amount=data.deductible_amount,
        document_id=data.document_id,
    )
    return schemas.AssetInsuranceResponse.model_validate(updated)

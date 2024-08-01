from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=schemas.DeviceRows)
async def read_devices(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve devices.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    if crud.user.is_superuser(current_user):
        devices = await crud.device.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.device.get_count(db, filters=filters)
    else:
        devices = await crud.device.get_rows_by_user(
            db, filters=filters, orders=orders,
            user=current_user, skip=skip, limit=limit
        )
        count = await crud.device.get_count_by_user(
            db, filters=filters, user=current_user
        )
    return {'data': jsonable_encoder(devices), 'total': count}


@router.post(
    '/',
    response_model=schemas.Device,
    status_code=status.HTTP_201_CREATED
)
async def create_device(
    *,
    db: AsyncSession = Depends(deps.get_db),
    device_in: schemas.DeviceCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new device.
    """
    device = await crud.device.create(
        db=db, obj_in=device_in
    )
    return device


@router.put('/{id}', response_model=schemas.Device)
async def update_device(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    device_in: schemas.DeviceUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an device.
    """
    device = await crud.device.get(db=db, id=id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    device = await crud.device.update(db=db, db_obj=device, obj_in=device_in)
    return device


@router.get('/{id}', response_model=schemas.Device)
async def read_device(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get device by ID.
    """
    device = await crud.device.get(db=db, id=id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    return device


@router.delete('/{id}', response_model=schemas.Device)
async def delete_device(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an device.
    """
    device = await crud.device.get(db=db, id=id)
    if not device:
        raise HTTPException(status_code=404, detail='Device not found')
    device = await crud.device.delete(db=db, id=id)
    return device

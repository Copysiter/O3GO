from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/', response_model=schemas.SettingRows)
async def read_settings(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve settings.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    settings = await crud.setting.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    count = await crud.setting.get_count(db, filters=filters)
    return {'data': settings, 'total': count}


@router.post(
    '/',
    response_model=schemas.Setting,
    status_code=status.HTTP_201_CREATED
)
async def create_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    setting_in: schemas.SettingCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new setting.
    """
    existing_setting = await crud.setting.get_by(db=db, key=setting_in.key)
    if existing_setting:
        raise HTTPException(
            status_code=400, detail="Setting with this key already exists"
        )
    options = []
    if setting_in.type == schemas.setting.Type.DROPDOWN:
        for row in setting_in.options.split('\n'):
            options.append(list(map(lambda x: x.strip(), row.split('|'))))
    setting_in.options = [
        models.SettingOption(name=row[0], value=row[-1]) for row in options
    ]
    setting = await crud.setting.create(
        db=db, obj_in=setting_in
    )

    return setting


@router.put('/{id}', response_model=schemas.Setting)
async def update_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    setting_in: schemas.SettingUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an setting.
    """
    setting = await crud.setting.get(db=db, id=id)
    if not setting:
        raise HTTPException(status_code=404, detail='Setting not found')
    options = []
    if setting_in.type == schemas.setting.Type.DROPDOWN:
        for row in setting_in.options.split('\n'):
            options.append(list(map(lambda x: x.strip(), row.split('|'))))
    setting_in.options = [
        models.SettingOption(name=row[0], value=row[-1]) for row in options
    ]
    setting = await crud.setting.update(db=db, db_obj=setting, obj_in=setting_in)

    return setting


@router.get('/{id}', response_model=schemas.Setting)
async def read_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get setting by ID.
    """
    setting = await crud.setting.get(db=db, id=id)
    if not setting:
        raise HTTPException(status_code=404, detail='Setting not found')
    return setting


@router.delete('/{id}', response_model=schemas.Setting)
async def delete_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an setting.
    """
    setting = await crud.setting.get(db=db, id=id)
    if not setting:
        raise HTTPException(status_code=404, detail='Setting not found')
    setting = await crud.setting.delete(db=db, id=id)
    return setting

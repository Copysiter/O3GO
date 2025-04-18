from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


def to_dict(setting_group: models.SettingGroup) -> dict:
    api_keys = list(setting_group.api_keys)
    values = setting_group.values
    setting_group = {
        k: v for k, v in setting_group.__dict__.items()
        if k in models.SettingGroup.__mapper__.c
    }
    for item in values:
        match item.setting.type:
            case schemas.setting.Type.TEXT | schemas.setting.Type.DROPDOWN:
                value = item.str_val
            case schemas.setting.Type.INTEGER:
                value = item.int_val
            case schemas.setting.Type.BOOLEAN:
                value = item.bool_val
            case schemas.setting.Type.PROXY:
                setting_group[f'{item.setting.key}_name'] = \
                    item.proxy_group.name if item.proxy_group else ''
                value = item.proxy_group_id or None
        setting_group[item.setting.key] = value
    setting_group.update({'api_keys': api_keys})
    return setting_group


async def get_values(
    db: AsyncSession, setting_group: schemas.SettingGroup
) -> List[dict]:
    values = []
    for key, value in setting_group.dict().items():
        if key not in {'id', 'name', 'description'}:
            setting = await crud.setting.get_by(db=db, key=key)
            if not setting:
                continue
            setting_value = models.SettingValue(
                setting_id=setting.id
            )
            match setting.type:
                case schemas.setting.Type.TEXT:
                    setting_value.str_val = value or None
                case schemas.setting.Type.INTEGER:
                    setting_value.int_val = value
                case schemas.setting.Type.BOOLEAN:
                    setting_value.bool_val = value
                case schemas.setting.Type.DROPDOWN:
                    setting_value.str_val = value
                case schemas.setting.Type.PROXY:
                    setting_value.proxy_group_id = value or None
            values.append(setting_value)
    return values

@router.get('/', response_model=schemas.SettingGroupRows)
async def read_setting_groups(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve setting_groups.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    setting_groups = await crud.setting_group.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    for i in range(len(setting_groups)):
        setting_groups[i] = to_dict(setting_groups[i])
    count = await crud.setting_group.get_count(db, filters=filters)
    return {
        'data': jsonable_encoder(setting_groups),
        'total': count
    }


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED
)
async def create_setting_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    setting_group_in: schemas.SettingGroupCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new setting_group.
    """
    values = await get_values(db, setting_group_in)
    keys = [
        models.SettingGroupApiKeys(api_key=key)
        for key in setting_group_in.api_keys
    ]
    setting_group = await crud.setting_group.create(db, obj_in={
        'name': setting_group_in.name,
        'check_period': setting_group_in.check_period,
        'description': setting_group_in.description,
        'is_active': setting_group_in.is_active,
        'values': values,
        'keys': keys
    })

    return jsonable_encoder(to_dict(setting_group))


@router.put('/{id}', response_model=schemas.SettingGroup)
async def update_setting_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    setting_group_in: schemas.SettingGroupUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an setting_group.
    """
    setting_group = await crud.setting_group.get(db=db, id=id)
    if not setting_group:
        raise HTTPException(status_code=404, detail='SettingGroup not found')
    values = await get_values(db, setting_group_in)
    keys = [
        models.SettingGroupApiKeys(api_key=key)
        for key in setting_group_in.api_keys
    ]
    setting_group = await crud.setting_group.update(
        db=db, db_obj=setting_group, obj_in={
            'name': setting_group_in.name,
            'check_period': setting_group_in.check_period,
            'description': setting_group_in.description,
            'is_active': setting_group_in.is_active,
            'values': values,
            'keys': keys
        }
    )

    return jsonable_encoder(to_dict(setting_group))


@router.get('/{id}', response_model=schemas.SettingGroup)
async def read_setting_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get setting_group by ID.
    """
    setting_group = await crud.setting_group.get(db=db, id=id)
    if not setting_group:
        raise HTTPException(status_code=404, detail='SettingGroup not found')
    return jsonable_encoder(to_dict(setting_group))


@router.delete('/{id}', response_model=schemas.SettingGroup)
async def delete_setting_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an setting_group.
    """
    setting_group = await crud.setting_group.get(db=db, id=id)
    if not setting_group:
        raise HTTPException(status_code=404, detail='SettingGroup not found')
    setting_group = await crud.setting_group.delete(db=db, id=id)
    return jsonable_encoder(to_dict(setting_group))

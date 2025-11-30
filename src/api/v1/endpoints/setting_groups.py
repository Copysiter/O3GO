from typing import Any, List, Dict  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


async def prepare_setting_values(
    db: AsyncSession, setting_group_data: schemas.SettingGroup
) -> List[models.SettingValue]:
    """
    Оптимизированная функция для подготовки значений настроек.
    Использует один запрос вместо N+1.
    """
    # Получаем все ключи настроек из входных данных, кроме служебных
    setting_keys = [
        key for key in setting_group_data.dict().keys()
        if key not in {'id', 'name', 'description', 'check_period', 'is_active', 'api_keys'}
    ]
    
    if not setting_keys:
        return []
    
    # Один запрос для получения всех нужных настроек
    stmt = select(models.Setting).where(models.Setting.key.in_(setting_keys))
    result = await db.execute(stmt)
    settings = {s.key: s for s in result.scalars().all()}
    
    values = []
    data_dict = setting_group_data.dict()
    
    for key, value in data_dict.items():
        if key in settings:
            setting = settings[key]
            setting_value = models.SettingValue(setting_id=setting.id)
            
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


@router.get('/', response_model=Dict[str, Any])
async def read_setting_groups(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]

    setting_groups_data = await crud.setting_group.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )

    count = await crud.setting_group.get_count(db, filters=filters)

    return {
        'data': setting_groups_data,
        'total': count
    }


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any]
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
    values = await prepare_setting_values(db, setting_group_in)
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

    # Загружаем созданный объект с полными связями
    setting_group = await crud.setting_group.get(db=db, id=setting_group.id)
    
    # Формируем полный ответ как в read_setting_group
    result = {
        'id': setting_group.id,
        'name': setting_group.name,
        'description': setting_group.description,
        'check_period': setting_group.check_period,
        'is_active': setting_group.is_active,
        'timestamp': setting_group.timestamp,
        'api_keys': [key.api_key for key in setting_group.keys] if setting_group.keys else []
    }
    
    # Добавляем значения настроек
    if setting_group.values:
        for value in setting_group.values:
            if value.setting:
                key = value.setting.key
                if value.setting.type == schemas.setting.Type.TEXT:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.INTEGER:
                    result[key] = value.int_val
                elif value.setting.type == schemas.setting.Type.BOOLEAN:
                    result[key] = value.bool_val
                elif value.setting.type == schemas.setting.Type.DROPDOWN:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.PROXY:
                    result[key] = value.proxy_group_id
                    result[f'{key}_name'] = (
                        value.proxy_group.name if value.proxy_group else ''
                    )
    
    return result


@router.post('/delete', response_model=List[Dict[str, Any]])
async def delete_setting_groups(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data: schemas.SettingGroupIds,
    # _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete setting groups.
    """
    deleted_groups = []
    for id in data.ids:
        setting_group = await crud.setting_group.get(db=db, id=id)
        if setting_group:
            # Сохраняем данные перед удалением
            group_name = setting_group.name
            # Удаляем без использования возвращаемого объекта
            await crud.setting_group.delete(db=db, id=id)
            deleted_groups.append({
                'id': id,
            })
        else:
            deleted_groups.append({
                'id': id,
            })
    return deleted_groups


@router.put('/status', response_model=List[Dict[str, Any]])
async def update_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data: schemas.SettingGroupStatusIds,
    # _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update setting groups status.
    """
    # Обновляем статус групп
    stmt = (
        update(models.SettingGroup)
        .where(models.SettingGroup.id.in_(data.ids))
        .values(is_active=data.is_active)
        .returning(models.SettingGroup.id, models.SettingGroup.name)
    )
    result = await db.execute(stmt)
    await db.commit()
    
    # Возвращаем только базовые данные для массового обновления статуса
    updated_groups = []
    updated_rows = result.fetchall()
    for row in updated_rows:
        updated_groups.append({
            'id': row.id,
            'is_active': data.is_active
        })
    
    return updated_groups


@router.put('/{id}', response_model=Dict[str, Any])
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
        
    values = await prepare_setting_values(db, setting_group_in)
    keys = [
        models.SettingGroupApiKeys(api_key=key)
        for key in setting_group_in.api_keys
    ]
    await crud.setting_group.update(
        db=db, db_obj=setting_group, obj_in={
            'name': setting_group_in.name,
            'check_period': setting_group_in.check_period,
            'description': setting_group_in.description,
            'is_active': setting_group_in.is_active,
            'values': values,
            'keys': keys
        }
    )

    # Загружаем обновленный объект с полными связями
    updated_setting_group = await crud.setting_group.get(db=db, id=id)

    
    result = {
        'id': updated_setting_group.id,
        'name': updated_setting_group.name,
        'description': updated_setting_group.description,
        'check_period': updated_setting_group.check_period,
        'is_active': updated_setting_group.is_active,
        'timestamp': updated_setting_group.timestamp,
        'api_keys': [key.api_key for key in updated_setting_group.keys] if updated_setting_group.keys else []
    }
    
    # Добавляем значения настроек
    if updated_setting_group.values:
        for value in updated_setting_group.values:
            if value.setting:
                key = value.setting.key
                if value.setting.type == schemas.setting.Type.TEXT:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.INTEGER:
                    result[key] = value.int_val
                elif value.setting.type == schemas.setting.Type.BOOLEAN:
                    result[key] = value.bool_val
                elif value.setting.type == schemas.setting.Type.DROPDOWN:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.PROXY:
                    result[key] = value.proxy_group_id
                    result[f'{key}_name'] = (
                        value.proxy_group.name if value.proxy_group else ''
                    )
    
    return result


@router.get('/{id}', response_model=Dict[str, Any])
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
    
    # Формируем полный ответ без рекурсивных связей
    result = {
        'id': setting_group.id,
        'name': setting_group.name,
        'description': setting_group.description,
        'check_period': setting_group.check_period,
        'is_active': setting_group.is_active,
        'timestamp': setting_group.timestamp,
        'api_keys': [key.api_key for key in setting_group.keys] if setting_group.keys else []
    }
    
    # Добавляем значения настроек как отдельные поля (как в read_setting_groups)
    if setting_group.values:
        for value in setting_group.values:
            if value.setting:
                key = value.setting.key
                if value.setting.type == schemas.setting.Type.TEXT:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.INTEGER:
                    result[key] = value.int_val
                elif value.setting.type == schemas.setting.Type.BOOLEAN:
                    result[key] = value.bool_val
                elif value.setting.type == schemas.setting.Type.DROPDOWN:
                    result[key] = value.str_val
                elif value.setting.type == schemas.setting.Type.PROXY:
                    result[key] = value.proxy_group_id
                    result[f'{key}_name'] = (
                        value.proxy_group.name if value.proxy_group else ''
                    )
    
    return result


@router.delete('/{id}', response_model=Dict[str, Any])
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
    
    # Сохраняем данные перед удалением
    group_name = setting_group.name
    await crud.setting_group.delete(db=db, id=id)
    
    # Возвращаем простые данные удаленного объекта
    return {
        'id': id,
        'name': group_name,
        'deleted': True
    }

from typing import Any, List  # noqa
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc

from api import deps  # noqa
import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=dict)
async def get_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    api_key: str,
    period: str = '30m',
    _=Depends(deps.check_api_key)
) -> Any:
    """Get settings"""
    match period[-1].lower():
        case 's':
            ts = datetime.utcnow() - timedelta(seconds=int(period[:-1]))
        case 'm':
            ts = datetime.utcnow() - timedelta(minutes=int(period[:-1]))
        case 'h':
            ts = datetime.utcnow() - timedelta(hours=int(period[:-1]))
        case 'd':
            ts = datetime.utcnow() - timedelta(days=int(period[:-1]))
        case _:
            ts = datetime.utcnow() - timedelta(seconds=int(period[:-1]))
    stmt = (
        select(models.SettingGroup).join(
            models.Number,
            models.Number.setting_group_id == models.SettingGroup.id
        ).where(
            models.Number.timestamp > ts
        ).where(
            models.SettingGroupApiKeys.api_key == api_key
        ).order_by(
            desc(models.Number.timestamp)
        ).limit(1)
    )
    result = await db.execute(stmt)
    setting_group = result.scalars().first()

    if not setting_group:
        stmt = (
            select(models.SettingGroup).where(
                models.SettingGroupApiKeys.api_key == api_key
            ).join(
                models.SettingGroupApiKeys,
                models.SettingGroup.id == models.SettingGroupApiKeys.group_id
            ).order_by(
                asc(models.SettingGroup.timestamp)
            ).limit(1)
        )

        result = await db.execute(stmt)
        setting_group = result.scalars().first()

    if not setting_group:
        raise HTTPException(status_code=404, detail='Settings not found')

    setting_group.timestamp = datetime.utcnow()
    db.add(setting_group)
    await db.commit()
    await db.refresh(setting_group)

    settings = {'id': setting_group.id}
    for s in setting_group.values:
        key = s.setting.key
        match s.setting.type:
            case schemas.setting.Type.TEXT:
                value = s.str_val
            case schemas.setting.Type.INTEGER:
                value = s.int_val
            case schemas.setting.Type.BOOLEAN:
                value = s.bool_val
            case schemas.setting.Type.PROXY:
                proxy = s.proxy_group.proxies[0] \
                    if s.proxy_group.proxies else None
                value = proxy.url if proxy else None
            case schemas.setting.Type.DROPDOWN:
                value = s.str_val
        settings[key] = value

    return settings

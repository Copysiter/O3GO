from typing import Any, List  # noqa
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy import asc, desc

from api import deps  # noqa
import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=dict)
async def get_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    api_key: str | None = None,
    id: int | None = None,
    _=Depends(deps.check_api_key)
) -> Any:
    """Get settings"""
    # stmt = (
    #     select(models.SettingGroup)
    #     .join(models.Number)
    #     .join(models.SettingGroup.keys)
    #     .where(models.SettingGroup.is_active.is_(True))
    #     .where(models.SettingGroupApiKeys.api_key == api_key)
    #     .where(
    #         models.Number.timestamp >
    #         func.now() - text(
    #             "make_interval(secs := coalesce(setting_group.check_period, 0))"
    #         )
    #     )
    #     .order_by(desc(models.Number.timestamp))
    #     .limit(1)
    # )
    # result = await db.execute(stmt)
    # setting_group = result.scalars().first()

    setting_group = None

    if id:
        setting_group = await crud.setting_group.get(db, id=id)
    elif api_key:
        stmt = (
            select(models.SettingGroup)
            .join(models.SettingGroupApiKeys)
            .where(models.SettingGroup.is_active == True)
            .where(models.SettingGroupApiKeys.api_key == api_key)
            .order_by(asc(models.SettingGroup.timestamp))
            .limit(1)
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
                # proxy = s.proxy_group.proxies[0] \
                #     if s.proxy_group.proxies else None
                proxy = await db.scalar(
                    select(models.Proxy)
                    .where(models.Proxy.group_id == s.proxy_group_id)
                    .order_by(models.Proxy.timestamp)
                    .limit(1)
                )
                value = proxy.url if proxy else None
                if proxy:
                    proxy.timestamp = datetime.utcnow()
                    db.add(proxy)
                    await db.commit()
                    await db.refresh(proxy)
            case schemas.setting.Type.DROPDOWN:
                value = s.str_val
        settings[key] = value

    return settings

from typing import Any, List  # noqa
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, update
from sqlalchemy import asc, desc
from sqlalchemy.orm import selectinload, noload

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

    try:
        setting_group = None

        if id:
            # Получаем setting_group БЕЗ автоматических joined загрузок
            stmt = (
                select(models.SettingGroup)
                .options(
                    noload(models.SettingGroup.keys),
                    # Отключаем lazy='joined'
                    selectinload(models.SettingGroup.values)
                    .selectinload(models.SettingValue.setting)
                    .selectinload(models.Setting.options)
                )
                .where(models.SettingGroup.id == id)
            )
            result = await db.execute(stmt)
            setting_group = result.scalar_one_or_none()

            if setting_group:
                # Обновляем timestamp
                await db.execute(
                    update(models.SettingGroup)
                    .where(models.SettingGroup.id == id)
                    .values(timestamp=datetime.utcnow())
                )

        elif api_key:
            # Получаем setting_group БЕЗ автоматических joined загрузок
            stmt = (
                select(models.SettingGroup)
                .join(models.SettingGroupApiKeys)
                .options(
                    noload(models.SettingGroup.keys),
                    # Отключаем lazy='joined'
                    selectinload(models.SettingGroup.values)
                    .selectinload(models.SettingValue.setting)
                    .selectinload(models.Setting.options)
                )
                .where(models.SettingGroup.is_active == True)
                .where(models.SettingGroupApiKeys.api_key == api_key)
                .order_by(asc(models.SettingGroup.timestamp))
                .limit(1)
            )
            result = await db.execute(stmt)
            setting_group = result.scalar_one_or_none()

            if setting_group:
                # Обновляем timestamp
                await db.execute(
                    update(models.SettingGroup)
                    .where(models.SettingGroup.id == setting_group.id)
                    .values(timestamp=datetime.utcnow())
                )

        if not setting_group:
            raise HTTPException(status_code=404, detail='Settings not found')

        # Получаем все proxy_group_ids для PROXY типов
        proxy_group_ids = list(set([
            s.proxy_group_id for s in setting_group.values
            if
            s.setting.type == schemas.setting.Type.PROXY and s.proxy_group_id
        ]))

        proxy_data = {}
        if proxy_group_ids:
            # UPDATE первых прокси по timestamp для каждой группы
            for group_id in proxy_group_ids:
                # Простой SELECT без joined загрузок для получения первого прокси
                first_proxy_stmt = (
                    select(models.Proxy)
                    .options(
                        noload(models.Proxy.keys),  # Отключаем ProxyApiKeys
                        noload(models.Proxy.group)  # Отключаем ProxyGroup
                    )
                    .where(models.Proxy.group_id == group_id)
                    .order_by(models.Proxy.timestamp)
                    .limit(1)
                )

                first_proxy_result = await db.execute(first_proxy_stmt)
                first_proxy = first_proxy_result.scalar_one_or_none()

                if first_proxy:
                    # UPDATE этого прокси
                    await db.execute(
                        update(models.Proxy)
                        .where(models.Proxy.id == first_proxy.id)
                        .values(timestamp=datetime.utcnow())
                    )
                    proxy_data[group_id] = first_proxy

        # Собираем настройки
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
                    proxy = proxy_data.get(
                        s.proxy_group_id) if s.proxy_group_id else None
                    value = proxy.url if proxy else None
                case schemas.setting.Type.DROPDOWN:
                    value = s.str_val
            settings[key] = value

        # ОДИН commit в конце
        await db.commit()

        return settings

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

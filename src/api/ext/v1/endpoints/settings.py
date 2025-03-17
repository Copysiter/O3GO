from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa
import crud, models, schemas  # noqa
from sqlalchemy.orm import relationship

router = APIRouter()


@router.get('/', response_model=dict)
async def get_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    api_key: str,
    _=Depends(deps.check_api_key)
) -> Any:
    orders = [{'field': 'timestamp', 'dir': 'asc'}]
    filters = [{'field': models.SettingGroupApiKeys.api_key, 'operator': 'eq', 'value': api_key}]
    setting_groups = await crud.setting_group.get_rows(
        db, filters=filters, orders=orders, limit=1
    )
    if not setting_groups:
        raise HTTPException(status_code=404, detail='Settings not found')
    setting_group = setting_groups[0]
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

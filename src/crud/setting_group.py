from typing import Any, List, Dict, Optional, Union  # noqa

from fastapi.encoders import jsonable_encoder

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.setting import SettingValue, SettingGroup, SettingGroupApiKeys  # noqa
from schemas.setting import SettingGroupCreate, SettingGroupUpdate # noqa


class CRUDSettingGroup(CRUDBase[SettingGroup, SettingGroupCreate, SettingGroupUpdate]):
    async def update(
        self, db: AsyncSession, *, db_obj: SettingGroup,
        obj_in: Union[SettingGroupUpdate, Dict[str, Any]]
    ) -> SettingGroup:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in db_obj.__dict__:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_api_keys(
        self, db: AsyncSession
    ) -> List[Any]:
        statement = select(
            SettingGroupApiKeys.api_key
        ).distinct().order_by(SettingGroupApiKeys.api_key.asc())
        result = await db.execute(statement=statement)

        return result.mappings().all()


setting_group = CRUDSettingGroup(SettingGroup)

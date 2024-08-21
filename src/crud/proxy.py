from typing import List

from typing import Any, Dict, Optional, Union  # noqa
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.user import User  # noqa
from models.proxy import Proxy, ProxyApiKeys  # noqa
from schemas.proxy import ProxyCreate, ProxyUpdate  # noqa


class CRUDProxy(CRUDBase[Proxy, ProxyCreate, ProxyUpdate]):
    async def get_by_url(
        self, db: AsyncSession, *, url: str
    ) -> Proxy:
        statement = (select(self.model).
                     where(self.model.url == url))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def update(
        self, db: AsyncSession, *, db_obj: Proxy,
        obj_in: Union[ProxyUpdate, Dict[str, Any]]
    ) -> Proxy:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if update_data.get('api_keys'):
            db_obj.keys = [ProxyApiKeys(api_key=key)
                           for key in update_data['api_keys']]
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_rows_by_user(
            self, db: AsyncSession, *, user: User,
            filters: list = None, orders: list = None,
            skip: int = 0, limit: int = 100
    ) -> List[Proxy]:
        filters.append({
            'field': 'api_keys', 'relationship': Proxy.keys,
            'operator': 'overlaps', 'value': list(user.api_keys)
        })
        return await self.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )

    async def get_count_by_user(
            self, db: AsyncSession, *, user: User, filters: dict = None
    ) -> int:
        filters.append({
            'field': ProxyApiKeys.api_key, 'relationship': Proxy.keys,
            'operator': 'overlaps', 'value': list(user.api_keys)
        })
        return await self.get_count(db, filters=filters)


proxy = CRUDProxy(Proxy)

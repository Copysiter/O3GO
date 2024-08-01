from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.user import User  # noqa
from models.device import Device  # noqa
from schemas.device import DeviceCreate, DeviceUpdate  # noqa


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    async def get_by_ext_id(
        self, db: AsyncSession, *, ext_id: str
    ) -> Device:
        statement = (select(self.model).
                     where(self.model.ext_id == ext_id))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_rows_by_user(
            self, db: AsyncSession, *, user: User,
            filters: list = None, orders: list = None,
            skip: int = 0, limit: int = 100
    ) -> List[Device]:
        filters.append({
            'field': 'api_key', 'operator': 'in', 'value': list(user.api_keys)
        })
        return await self.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )

    async def get_count_by_user(
            self, db: AsyncSession, *, user: User, filters: dict = None
    ) -> int:
        filters.append({
            'field': 'api_key', 'operator': 'in', 'value': list(user.api_keys)
        })
        return await self.get_count(db, filters=filters)


device = CRUDDevice(Device)

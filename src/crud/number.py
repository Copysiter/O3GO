from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, not_
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models import User, Number, Reg  # noqa
from schemas import NumberCreate, NumberUpdate  # noqa


class CRUDNumber(CRUDBase[Number, NumberCreate, NumberUpdate]):
    async def get_by_number(
        self, db: AsyncSession, number: str
    ) -> Optional[Number]:
        statement = select(self.model).where(self.model.number == number)
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_by_service(
        self, db: AsyncSession, service: int,
        last_minutes: int | None = None, filter: dict | None = None
    ) -> Optional[Number]:
        where = [not_(self.model.regs.any(Reg.service == service))]
        if last_minutes:
            timestamp = datetime.utcnow() - timedelta(minutes=last_minutes)
            where.append(self.model.timestamp >= timestamp)
        if filter:
            for k, v in filter.items():
                if k == 'where_service':
                    k = 'service_alias'
                elif k == 'where_device_id':
                    k = 'device_ext_id'
                else:
                    k = k.replace('where_', '')
                if v is not None:
                    where.append(getattr(self.model, k) == v)
        statement = (select(self.model).
                     where(*where).
                     order_by(func.random()).limit(1))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_all_by_user(
        self, db: AsyncSession, *, user: User,
        filters: list = None, orders: list = None
    ) -> List[Number]:
        filters.append({
            'field': 'api_key', 'operator': 'in', 'value': list(user.api_keys)
        })
        return await self.get_all(db, filters=filters, orders=orders)

    async def get_rows_by_user(
        self, db: AsyncSession, *, user: User,
        filters: list = None, orders: list = None,
        skip: int = 0, limit: int = 100
    ) -> List[Number]:
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


number = CRUDNumber(Number)

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, not_
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models import Number, Reg  # noqa
from schemas import NumberCreate, NumberUpdate  # noqa


class CRUDNumber(CRUDBase[Number, NumberCreate, NumberUpdate]):
    async def get_by_number(
        self, db: AsyncSession, number: int
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
        print()
        print(statement)
        print()
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()


number = CRUDNumber(Number)

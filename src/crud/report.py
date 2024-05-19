from datetime import date, datetime, timedelta
from typing import List, Any
from sqlalchemy import select, func, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, distinct

from core.config import settings  # noqa
from crud.base import CRUDBase  # noqa
from models import Report, Device  # noqa
from schemas import ReportCreate, ReportUpdate  # noqa


class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    async def get_rows(
        self, db: AsyncSession, *, skip=0, limit=100,
        filters: list = None, orders: list = None
    ) -> List[Any]:
        filter_list = []

        for i in range(len(filters)):
            if filters[i]['field'] == 'period' and filters[i]['value']:
                d = int(filters[i]['value'][:-1])
                filter_list.append(
                    self.model.date >= date.today() - timedelta(days=d))
                if d > 0:
                    filter_list.append(self.model.date < date.today())
                del filters[i]
            elif filters[i]['field'] == 'date':
                filters[i]['value'] = datetime.strptime(
                    filters[i]['value'], '%Y-%m-%d %H:%M:%S').date()
        filter_list += self.get_filters(filters) if filters else []
        order_list = self.get_orders(orders) if orders else []

        statement = (select(
                        self.model.api_key, self.model.device_id).
                     where(*filter_list).
                     group_by(self.model.api_key, self.model.device_id).
                     order_by(*order_list).
                     offset(skip).limit(limit))

        rows = (await db.execute(statement=statement)).all()
        keys = [row[0] for row in rows]
        ids = [row[1] for row in rows]
        pks = [(row[0], row[1]) for row in rows]
        # ts = {(row[0], row[1]): row[2] for row in rows}

        statement = (select(
                        self.model.api_key,
                        self.model.device_id, self.model.service_id,
                        func.sum(self.model.start_count).label('start_count'),
                        func.sum(self.model.number_count).label('number_count'),
                        func.sum(self.model.code_count).label('code_count'),
                        func.sum(self.model.no_code_count).label('no_code_count'),
                        func.sum(self.model.bad_count).label('bad_count'),
                        func.max(self.model.timestamp).label('timestamp'),
                        func.string_agg(distinct(Device.ext_id), None).label('device_ext_id'),
                        func.string_agg(distinct(Device.name), None).label('device_name'),
                        func.string_agg(distinct(Device.operator), None).label('device_operator'),
                        func.bool_and(Device.root).label('device_root')).
                     join(Device, Device.id == self.model.device_id).
                     where(
                        tuple_(self.model.api_key, self.model.device_id).in_(pks),
                        *filter_list).
                     group_by(
                        self.model.api_key, self.model.device_id,
                        self.model.service_id).
                     order_by(*order_list))
        rows = await db.execute(statement=statement)
        stats = {}
        for row in rows.mappings().all():
            pk = (row.api_key, row.device_id)
            if pk not in stats:
                stats[pk] = {
                    'api_key': row.api_key,
                    'device_id': row.device_id,
                    'device_ext_id': row.device_ext_id,
                    'device_name': row.device_name,
                    'device_operator': row.device_operator,
                    'device_root': row.device_root,
                    'timestamp': row.timestamp
                }
            for c in ('start_count', 'number_count', 'code_count',
                      'no_code_count', 'bad_count'):
                stats[pk][f'{c}_{row.service_id}'] = getattr(row, c)
        return list(stats.values())

    async def get_count(
        self, db: AsyncSession, *, filters: dict = None
    ) -> List[Any]:
        filter_list = self.get_filters(filters) if filters else []
        statement = select(
            func.count(
                func.distinct(
                    self.model.api_key, self.model.device_id
                )
            )
        ).where(*filter_list)
        results = await db.execute(statement=statement)
        return results.scalar_one()

    async def get_by(
        self, db: AsyncSession, *, api_key: str,
            device_id: int, service_id: int, date: date
    ) -> Report:
        statement = (select(self.model).
                     where(self.model.api_key == api_key).
                     where(self.model.device_id == device_id).
                     where(self.model.service_id == service_id).
                     where(self.model.date == date))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_last(
        self, db: AsyncSession, *, device_id: int,
            service_id: int, days: int = 7
    ) -> Report:
        pass


report = CRUDReport(Report)

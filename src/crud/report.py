import json

from datetime import date, datetime, timedelta
from typing import List, Any
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, distinct

from core.config import settings  # noqa
from crud.base import CRUDBase  # noqa
from models import User, Report, Device, Service  # noqa
from schemas import ReportCreate, ReportUpdate  # noqa


class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    def filter_modify(self, filters):
        filter_list = []
        for i in range(len(filters)):
            if filters[i]['field'] == 'period' and filters[i]['value']:
                d = int(filters[i]['value'][:-1])
                filter_list.append({
                    'field': 'date',
                    'operator': 'gte',
                    'value': date.today() - timedelta(days=d)
                })
                # filter_list.append(
                # self.model.date >= date.today() - timedelta(days=d))
                if d > 0:
                    filter_list.append({
                        'field': 'date',
                        'operator': 'lt',
                        'value': date.today()
                    })
                    # filter_list.append(self.model.date < date.today())
            elif filters[i]['field'] == 'date' and \
                    isinstance(filters[i]['value'], str):
                filters[i]['value'] = datetime.strptime(
                    filters[i]['value'], '%Y-%m-%d %H:%M:%S').date()
                filter_list.append(filters[i])
            elif filters[i]['field'] in (
                    'device_name', 'device_operator', 'device_ext_id'):
                field = filters[i]['field'].replace('device_', '')
                filter_list.append({
                    'field': getattr(Device, field, None),
                    'relationship': self.model.device,
                    'operator': filters[i]['operator'],
                    'value': filters[i]['value']
                })
            elif filters[i]['field'] in self.model.__table__.c:
                if filters[i]['field'] == 'service_id' \
                        and isinstance(filters[i]['value'], str):
                    filters[i]['value'] = json.loads(filters[i]['value'])
                filter_list.append(filters[i])

        return filter_list

    def order_modify(self, orders):
        order_list = []
        if not orders:
            order_list.append(
                {'field': func.max(self.model.timestamp), 'dir': 'desc'})
        for i in range(len(orders)):
            match orders[i]['field']:
                case str(x) if 'count' in x:
                    end = orders[i]['field'].rfind('_')
                    field = func.sum(
                        getattr(self.model, orders[i]['field'][:end]))
                case 'timestamp':
                    field = func.max(self.model.timestamp)
                case 'ts_1':
                    field = func.max(self.model.ts_1)
                case _:
                    field = orders[i]['field']
            order_list.append(
                {'field': field, 'dir': orders[i]['dir']})

        return order_list

    async def get_rows(
        self, db: AsyncSession, *, skip=0, limit=100,
        filters: list = None, orders: list = None
    ) -> List[Any]:
        order_list = self.get_orders(self.order_modify(orders))
        filter_list = self.get_filters(self.filter_modify(filters))

        statement = (select(
                        self.model.api_key, self.model.device_id).
                     join(Device, Device.id == self.model.device_id).
                     where(*filter_list).
                     group_by(self.model.api_key, self.model.device_id).
                     order_by(*order_list).
                     offset(skip).limit(limit))

        rows = (await db.execute(statement=statement)).all()
        pks = [(row[0], row[1]) for row in rows]

        statement = (select(
                self.model.api_key,
                self.model.device_id, self.model.service_id,
                func.sum(self.model.start_count).label('start_count'),
                func.sum(self.model.number_count).label('number_count'),
                func.sum(self.model.code_count).label('code_count'),
                func.sum(self.model.no_code_count).label('no_code_count'),
                func.sum(self.model.bad_count).label('bad_count'),
                func.max(self.model.timestamp).label('timestamp'),
                func.max(self.model.ts_1).label('ts_1'),
                func.string_agg(
                    distinct(Device.ext_id), None).label('device_ext_id'),
                func.string_agg(
                    distinct(Device.name), None).label('device_name'),
                func.string_agg(
                    distinct(Device.operator), None).label('device_operator'),
                func.bool_and(Device.root).label('device_root'),
                func.string_agg(
                    distinct(self.model.info_1), None).label('info_1'),
                func.string_agg(
                    distinct(self.model.info_2), None).label('info_2'),
                func.string_agg(
                    distinct(self.model.info_3), None).label('info_3')
            ).join(Device, Device.id == self.model.device_id).
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
                    'timestamp': row.timestamp,
                    'timedelta': (datetime.utcnow() -
                                  row.timestamp).total_seconds(),
                    'ts_1': row.ts_1,
                    'info_1': row.info_1,
                    'info_2': row.info_2,
                    'info_3': row.info_3,
                }
            for c in ('start_count', 'number_count', 'code_count',
                      'no_code_count', 'bad_count'):
                stats[pk][f'{c}_{row.service_id}'] = getattr(row, c)
        return list(stats.values())

    async def get_count(
        self, db: AsyncSession, *, filters: dict = None
    ) -> List[Any]:
        filter_list = self.get_filters(self.filter_modify(filters))
        statement = select(
            func.count(
                func.distinct(
                    self.model.api_key, self.model.device_id
                )
            )
        ).where(*filter_list)
        results = await db.execute(statement=statement)
        return results.scalar_one()

    async def get_rows_by_user(
            self, db: AsyncSession, *, user: User,
            filters: list = None, orders: list = None,
            skip: int = 0, limit: int = 100
    ) -> List[Any]:
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

    async def get_bad(
        self, db: AsyncSession, begin_ts: datetime, end_ts: datetime
    ) -> List[Any]:
        statement = (select(
                self.model.api_key,
                self.model.device_id, self.model.service_id,
                func.sum(self.model.start_count).label('start_count'),
                func.sum(self.model.number_count).label('number_count'),
                func.sum(self.model.code_count).label('code_count'),
                func.sum(self.model.no_code_count).label('no_code_count'),
                func.sum(self.model.bad_count).label('bad_count'),
                func.max(self.model.timestamp).label('timestamp'),
                func.max(self.model.ts_1).label('ts_1'),
                func.string_agg(
                    distinct(Device.ext_id), None).label('device_ext_id'),
                func.string_agg(
                    distinct(Device.name), None).label('device_name'),
                func.string_agg(
                    distinct(Device.operator), None).label('device_operator'),
                func.bool_and(Device.root).label('device_root'),
                func.string_agg(
                    distinct(Service.name), None).label('service_name'),
            ).
            join(Device, Device.id == self.model.device_id).
            join(Service, Service.id == self.model.service_id).
            where(
                self.model.timestamp >= begin_ts,
                self.model.timestamp < end_ts,
            ).
            group_by(
                self.model.api_key, self.model.device_id,
                self.model.service_id).
            having(func.sum(self.model.start_count) > 0).
            having(func.sum(self.model.code_count) < func.sum(
                self.model.start_count)).
            having(func.sum(self.model.code_count) < 2).
            order_by(func.max(self.model.timestamp)))

        result = await db.execute(statement=statement)

        return result.mappings().all()

    async def get_api_keys(
        self, db: AsyncSession
    ) -> List[Any]:
        statement = select(
            self.model.api_key).distinct().order_by(self.model.api_key.asc())
        result = await db.execute(statement=statement)

        return result.mappings().all()


report = CRUDReport(Report)

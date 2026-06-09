from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import User
from models.analytics import Analytics
from schemas.analytics import AnalyticsCreate, AnalyticsUpdate


class CRUDAnalytics(CRUDBase[Analytics, AnalyticsCreate, AnalyticsUpdate]):
    async def get_rows_by_user(
        self, db: AsyncSession, *, user: User,
        filters: list = None, orders: list = None,
        skip: int = 0, limit: int = 100
    ) -> List[Analytics]:
        filters = filters or []
        filters.append({
            'field': 'user_id', 'operator': 'eq', 'value': user.id
        })
        return await self.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )

    async def get_count_by_user(
        self, db: AsyncSession, *, user: User, filters: list = None
    ) -> int:
        filters = filters or []
        filters.append({
            'field': 'user_id', 'operator': 'eq', 'value': user.id
        })
        return await self.get_count(db, filters=filters)

    async def mark_running(
        self, db: AsyncSession, *, db_obj: Analytics
    ) -> Analytics:
        return await self.update(
            db=db, db_obj=db_obj, obj_in={'status': 'running', 'error': None}
        )

    async def mark_done(
        self, db: AsyncSession, *, db_obj: Analytics,
        html_path: str, xlsx_path: str, html_filename: str, xlsx_filename: str
    ) -> Analytics:
        return await self.update(db=db, db_obj=db_obj, obj_in={
            'status': 'done',
            'html_path': html_path,
            'xlsx_path': xlsx_path,
            'html_filename': html_filename,
            'xlsx_filename': xlsx_filename,
            'finished_at': datetime.utcnow(),
            'error': None,
        })

    async def mark_failed(
        self, db: AsyncSession, *, db_obj: Analytics, error: str
    ) -> Analytics:
        return await self.update(db=db, db_obj=db_obj, obj_in={
            'status': 'failed',
            'error': error[:4000],
            'finished_at': datetime.utcnow(),
        })


analytics = CRUDAnalytics(Analytics)

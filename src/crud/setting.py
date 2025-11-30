from typing import Any, List, Dict, Optional, Union  # noqa

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.setting import SettingOption, Setting  # noqa
from schemas.setting import SettingCreate, SettingUpdate # noqa


class CRUDSetting(CRUDBase[Setting, SettingCreate, SettingUpdate]):
    async def get_rows(
        self, db: AsyncSession, *, skip=0, limit=100,
        filters: list = None, orders: list = None
    ) -> List[Setting]:
        filter_list = self.get_filters(filters) if filters else []
        order_list = self.get_orders(orders) if orders else []

        statement = (
            select(self.model)
            .options(
                selectinload(Setting.options)  # Предзагружаем options
            )
            .where(*filter_list)
            .order_by(*order_list)
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.unique().scalars().all()

    async def get(
        self, db: AsyncSession, *, id: int, options: List = None
    ) -> Optional[Setting]:
        """Получить настройку с предзагрузкой options"""
        statement = (
            select(self.model)
            .options(selectinload(Setting.options))  # Предзагружаем options
            .where(self.model.id == id)
        )
        result = await db.execute(statement=statement)
        return result.unique().scalar_one_or_none()


setting = CRUDSetting(Setting)

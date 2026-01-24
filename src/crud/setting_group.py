from typing import Any, List, Dict, Optional, Union  # noqa

from fastapi.encoders import jsonable_encoder

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.setting import SettingValue, SettingGroup, SettingGroupApiKeys  # noqa
from schemas.setting import SettingGroupCreate, SettingGroupUpdate # noqa


class CRUDSettingGroup(
    CRUDBase[SettingGroup, SettingGroupCreate, SettingGroupUpdate]
):
    async def get_rows(
        self, db: AsyncSession, *, skip=0, limit=100,
        filters: list = None, orders: list = None
    ) -> List[Dict[str, Any]]:
        """
        Оптимизированный метод для загрузки данных групп настроек для grid'а
        Использует минимальное количество запросов с selectinload
        """
        filter_list = self.get_filters(filters) if filters else []
        order_list = self.get_orders(orders) if orders else []

        # Основной запрос с предзагрузкой только необходимых связей
        statement = (
            select(self.model)
            .options(
                # Загружаем API ключи (обычно мало записей)
                selectinload(SettingGroup.keys),
                # Загружаем значения настроек с их настройками и proxy группами
                selectinload(SettingGroup.values)
                .selectinload(SettingValue.setting),
                selectinload(SettingGroup.values)
                .selectinload(SettingValue.proxy_group),
                # Загружаем связанный сервис
                selectinload(SettingGroup.service_obj)
            )
            .where(*filter_list)
            .order_by(*order_list)
            .offset(skip)
            .limit(limit)
        )

        results = await db.execute(statement=statement)
        setting_groups = results.unique().scalars().all()

        # Преобразуем в формат для grid'а без дополнительных запросов к БД
        grid_data = []
        for sg in setting_groups:
            # Базовые поля группы настроек
            group_dict = {
                'id': sg.id,
                'name': sg.name,
                'service': sg.service,
                'service_obj': {
                    'id': sg.service_obj.id,
                    'alias': sg.service_obj.alias,
                    'name': sg.service_obj.name,
                    'color_bg': sg.service_obj.color_bg,
                    'color_txt': sg.service_obj.color_txt,
                    'is_active': sg.service_obj.is_active
                } if sg.service_obj else None,
                'description': sg.description,
                'check_period': sg.check_period,
                'is_active': sg.is_active,
                'timestamp': sg.timestamp,
                # API ключи (уже загружены через selectinload)
                'api_keys': [
                    key.api_key for key in sg.keys
                ] if sg.keys else []
            }

            # Добавляем значения настроек как отдельные поля
            if sg.values:
                for value in sg.values:
                    if value.setting:
                        setting_key = value.setting.key

                        # В зависимости от типа настройки берем нужное значение
                        if value.setting.type == 0 or value.setting.type == 3:  # TEXT/DROPDOWN
                            group_dict[setting_key] = value.str_val
                        elif value.setting.type == 1:  # INTEGER
                            group_dict[setting_key] = value.int_val
                        elif value.setting.type == 2:  # BOOLEAN
                            group_dict[setting_key] = value.bool_val
                        elif value.setting.type == 4:  # PROXY
                            # Для proxy добавляем и ID и название
                            group_dict[setting_key] = value.proxy_group_id
                            group_dict[f'{setting_key}_name'] = (
                                value.proxy_group.name if value.proxy_group else ''
                            )

            grid_data.append(group_dict)

        return grid_data

    async def get(
        self, db: AsyncSession, *, id: int
    ) -> Optional[SettingGroup]:
        """
        Получение группы настроек с загруженными связями для отдельных эндпоинтов
        """
        statement = (
            select(self.model)
            .options(
                selectinload(SettingGroup.keys),
                selectinload(SettingGroup.values)
                .selectinload(SettingValue.setting),
                selectinload(SettingGroup.values)
                .selectinload(SettingValue.proxy_group),
                selectinload(SettingGroup.service_obj)
            )
            .where(self.model.id == id)
        )
        result = await db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def update(
        self, db: AsyncSession, *, db_obj: SettingGroup,
        obj_in: Union[SettingGroupUpdate, Dict[str, Any]], commit: bool = True
    ) -> SettingGroup:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in db_obj.__dict__:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        if commit:
            await db.commit()
        else:
            await db.flush()
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

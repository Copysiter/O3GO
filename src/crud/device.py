from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
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


device = CRUDDevice(Device)

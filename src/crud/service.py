from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.service import Service  # noqa
from schemas.service import ServiceCreate, ServiceUpdate  # noqa


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    async def get_by_alias(
        self, db: AsyncSession, *, alias: str
    ) -> Service:
        statement = (select(self.model).where(self.model.alias == alias))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()


service = CRUDService(Service)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.proxy import Proxy  # noqa
from schemas.proxy import ProxyCreate, ProxyUpdate  # noqa


class CRUDProxy(CRUDBase[Proxy, ProxyCreate, ProxyUpdate]):
    async def get_by_url(
        self, db: AsyncSession, *, url: str
    ) -> Proxy:
        statement = (select(self.model).
                     where(self.model.url == url))
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()


proxy = CRUDProxy(Proxy)

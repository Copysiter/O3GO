from typing import List

from typing import Any, Dict, Optional, Union  # noqa
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.user import User  # noqa
from models.proxy import ProxyGroup  # noqa
from schemas.proxy_group import ProxyGroupCreate, ProxyGroupUpdate  # noqa


class CRUDProxy(CRUDBase[ProxyGroup, ProxyGroupCreate, ProxyGroupUpdate]):
    pass


proxy_group = CRUDProxy(ProxyGroup)

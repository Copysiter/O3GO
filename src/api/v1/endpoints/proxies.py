from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, Body, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=schemas.ProxyRows)
async def read_proxies(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve proxies.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    proxies = await crud.proxy.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    count = await crud.proxy.get_count(db, filters=filters)
    return {'data': jsonable_encoder(proxies), 'total': count}


@router.post(
    '/',
    response_model=schemas.Proxy,
    status_code=status.HTTP_201_CREATED
)
async def create_proxy(
    *,
    db: AsyncSession = Depends(deps.get_db),
    proxy_in: schemas.ProxyCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new proxy.
    """
    proxy = await crud.proxy.create(
        db=db, obj_in=proxy_in
    )
    return proxy


@router.post('/delete', response_model=List[schemas.Proxy])
async def delete_proxies(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data: schemas.ProxyIds,
    # _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an proxies.
    """
    proxies = []
    for id in data.ids:
        proxy = await crud.proxy.delete(db=db, id=id)
        proxies.append(proxy)
    return proxies


@router.put('/{id}', response_model=schemas.Proxy)
async def update_proxy(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    proxy_in: schemas.ProxyUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an proxy.
    """
    proxy = await crud.proxy.get(db=db, id=id)
    if not proxy:
        raise HTTPException(status_code=404, detail='Proxy not found')
    proxy = await crud.proxy.update(db=db, db_obj=proxy, obj_in=proxy_in)
    return proxy


@router.get('/{id}', response_model=schemas.Proxy)
async def read_proxy(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get proxy by ID.
    """
    proxy = await crud.proxy.get(db=db, id=id)
    if not proxy:
        raise HTTPException(status_code=404, detail='Proxy not found')
    return proxy


@router.delete('/{id}', response_model=schemas.Proxy)
async def delete_proxy(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an proxy.
    """
    proxy = await crud.proxy.get(db=db, id=id)
    if not proxy:
        raise HTTPException(status_code=404, detail='Proxy not found')
    proxy = await crud.proxy.delete(db=db, id=id)
    return proxy

from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, Body, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/', response_model=schemas.ProxyGroupRows)
async def read_proxy_groups(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve proxy groups.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    if crud.user.is_superuser(current_user):
        proxy_groups = await crud.proxy_group.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.proxy_group.get_count(db, filters=filters)
    else:
        # proxy_groups = await crud.proxy_group.get_rows_by_user(
        #     db, filters=filters, orders=orders,
        #     user=current_user, skip=skip, limit=limit
        # )
        # count = await crud.proxy_group.get_count_by_user(
        #     db, filters=filters, user=current_user
        # )
        proxy_groups = await crud.proxy_group.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.proxy_group.get_count(db, filters=filters)
    return {'data': jsonable_encoder(proxy_groups), 'total': count}


@router.post(
    '/',
    response_model=schemas.ProxyGroup,
    status_code=status.HTTP_201_CREATED
)
async def create_proxy_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    proxy_group_in: schemas.ProxyGroupCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new proxy group.
    """
    proxies = []
    if proxy_group_in.proxies:
        for url in proxy_group_in.proxies.split():
            proxy = await crud.proxy.get_by(db=db, url=url)
            if not proxy:
                proxy = models.Proxy(url=url)
            proxies.append(proxy)
    proxy_group_in.proxies = proxies
    proxy_group = await crud.proxy_group.create(
        db=db, obj_in=proxy_group_in
    )
    return jsonable_encoder(proxy_group)


@router.put('/{id}', response_model=schemas.ProxyGroup)
async def update_proxy_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    proxy_group_in: schemas.ProxyGroupUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a proxy group.
    """
    proxy_group = await crud.proxy_group.get(db=db, id=id)
    proxy_urls = {proxy.url: proxy for proxy in proxy_group.proxies}
    proxies = []
    if proxy_group_in.proxies:
        for url in proxy_group_in.proxies.split():
            if url in proxy_urls:
                proxies.append(proxy_urls[url])
            else:
                proxy = await crud.proxy.get_by(db=db, url=url)
                if not proxy:
                    proxy = models.Proxy(url=url)
                proxies.append(proxy)
    proxy_group_in.proxies = proxies
    if not proxy_group:
        raise HTTPException(status_code=404, detail='Proxy Group not found')
    proxy_group = await crud.proxy_group.update(db=db, db_obj=proxy_group, obj_in=proxy_group_in)

    return jsonable_encoder(proxy_group)


@router.get('/{id}', response_model=schemas.ProxyGroup)
async def read_proxy_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get proxy group by ID.
    """
    proxy_group = await crud.proxy_group.get(db=db, id=id)
    if not proxy_group:
        raise HTTPException(status_code=404, detail='Proxy Group not found')
    return proxy_group


@router.delete('/{id}', response_model=schemas.ProxyGroup)
async def delete_proxy_group(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a proxy group.
    """
    proxy_group = await crud.proxy_group.get(db=db, id=id)
    if not proxy_group:
        raise HTTPException(status_code=404, detail='Proxy Group not found')
    proxy_group = await crud.proxy_group.delete(db=db, id=id)
    return proxy_group

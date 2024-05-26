from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=schemas.ServiceRows)
async def read_services(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve services.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    services = await crud.service.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    count = await crud.service.get_count(db, filters=filters)
    return {'data': jsonable_encoder(services), 'total': count}


@router.post(
    '/',
    response_model=schemas.Service,
    status_code=status.HTTP_201_CREATED
)
async def create_service(
    *,
    db: AsyncSession = Depends(deps.get_db),
    service_in: schemas.ServiceCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new service.
    """
    service = await crud.service.create(
        db=db, obj_in=service_in
    )
    return service


@router.put('/{id}', response_model=schemas.Service)
async def update_service(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    service_in: schemas.ServiceUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an service.
    """
    service = await crud.service.get(db=db, id=id)
    if not service:
        raise HTTPException(status_code=404, detail='Service not found')
    service = await crud.service.update(db=db, db_obj=service, obj_in=service_in)
    return service


@router.get('/{id}', response_model=schemas.Service)
async def read_service(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get service by ID.
    """
    service = await crud.service.get(db=db, id=id)
    if not service:
        raise HTTPException(status_code=404, detail='Service not found')
    return service


@router.delete('/{id}', response_model=schemas.Service)
async def delete_service(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an service.
    """
    service = await crud.service.get(db=db, id=id)
    if not service:
        raise HTTPException(status_code=404, detail='Service not found')
    service = await crud.service.delete(db=db, id=id)
    return service

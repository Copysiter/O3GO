from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=schemas.NumberRows)
async def read_numbers(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve numbers.
    """
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    if crud.user.is_superuser(current_user):
        numbers = await crud.number.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.number.get_count(db, filters=filters)
    else:
        numbers = await crud.number.get_rows_by_user(
            db, filters=filters, orders=orders,
            user=current_user, skip=skip, limit=limit
        )
        count = await crud.number.get_count_by_user(
            db, filters=filters, user=current_user
        )
    return {'data': jsonable_encoder(numbers), 'total': count}
from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/') # , response_model=schemas.DeviceRows)
async def get_report(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve reports.
    """
    report = await crud.report.get_rows(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    count = await crud.report.get_count(db, filters=filters)
    return {'data': jsonable_encoder(report), 'total': count}


@router.get('/bad') # , response_model=schemas.DeviceRows)
async def get_bad_report(
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Retrieve bad reports.
    """
    report = await crud.report.get_bad(db)
    return {'data': jsonable_encoder(report)}

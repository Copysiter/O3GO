from typing import Any, List  # noqa
from datetime import datetime

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
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve reports.
    """
    filtered_map: dict = {}
    for f in filters:
        field = f.get("field")
        if field in filtered_map and f.get("operator") == "eq":
            if isinstance(filtered_map[field]["value"], list):
                filtered_map[field]["value"].append(f.get("value"))
            else:
                filtered_map[field].update({
                    "field": field, "operator": "overlaps", "value": [
                        filtered_map[field]["value"], f.get("value")
                    ]
                })
        else:
            filtered_map.update({field: f})

    filters = list(filtered_map.values())

    if crud.user.is_superuser(current_user):
        report = await crud.report.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.report.get_count(db, filters=filters)
    else:
        report = await crud.report.get_rows_by_user(
            db, filters=filters, orders=orders,
            user=current_user, skip=skip, limit=limit
        )
        count = await crud.report.get_count_by_user(
            db, filters=filters, user=current_user
        )
    return {'data': jsonable_encoder(report), 'total': count}


@router.get('/bad') # , response_model=schemas.DeviceRows)
async def get_bad_report(
    db: AsyncSession = Depends(deps.get_db), *,
    begin: str, end: str,
) -> Any:
    """
    Retrieve bad reports.
    """
    try:
        begin_ts = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S')
        end_ts = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    report = await crud.report.get_bad(db, begin_ts, end_ts)
    return {'data': jsonable_encoder(report)}

from pathlib import Path
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps

import crud
import models
import schemas


router = APIRouter()


def _assert_can_access(item: models.Analytics, user: models.User) -> None:
    if not crud.user.is_superuser(user) and item.created_by_id != user.id:
        raise HTTPException(status_code=403, detail='Not enough permissions')


def _unlink(path: str | None) -> None:
    if not path:
        return
    file_path = Path(path)
    if file_path.exists() and file_path.is_file():
        file_path.unlink()


@router.get('/', response_model=schemas.AnalyticsRows)
async def read_analytics(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if not orders:
        orders = [{'field': 'id', 'dir': 'desc'}]
    if crud.user.is_superuser(current_user):
        rows = await crud.analytics.get_rows(
            db, filters=filters, orders=orders, skip=skip, limit=limit
        )
        count = await crud.analytics.get_count(db, filters=filters)
    else:
        rows = await crud.analytics.get_rows_by_user(
            db, filters=filters, orders=orders, skip=skip, limit=limit,
            user=current_user
        )
        count = await crud.analytics.get_count_by_user(
            db, filters=filters, user=current_user
        )
    return {'data': jsonable_encoder(rows), 'total': count}


@router.post('/run', response_model=schemas.Analytics, status_code=status.HTTP_201_CREATED)
async def run_analytics(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data: schemas.AnalyticsRunRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    item = await crud.analytics.create(db=db, obj_in={
        'period': data.period or 'Current selection',
        'status': 'pending',
        'created_by_id': current_user.id,
    })
    from tasks import analytics_handler
    analytics_handler.delay(item.id, data.filters, current_user.id, item.period)
    return item


@router.get('/{id}', response_model=schemas.Analytics)
async def read_analytics_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    item = await crud.analytics.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Analytics not found')
    _assert_can_access(item, current_user)
    return item


@router.get('/{id}/html')
async def read_analytics_html(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    item = await crud.analytics.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Analytics not found')
    _assert_can_access(item, current_user)
    if item.status != 'done' or not item.html_path or not Path(item.html_path).exists():
        raise HTTPException(status_code=404, detail='HTML report not found')
    return FileResponse(
        item.html_path,
        media_type='text/html; charset=utf-8',
        filename=item.html_filename or f'analytics_{item.id}.html'
    )


@router.get('/{id}/xlsx')
async def read_analytics_xlsx(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    item = await crud.analytics.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Analytics not found')
    _assert_can_access(item, current_user)
    if item.status != 'done' or not item.xlsx_path or not Path(item.xlsx_path).exists():
        raise HTTPException(status_code=404, detail='XLSX report not found')
    return FileResponse(
        item.xlsx_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=item.xlsx_filename or f'analytics_{item.id}.xlsx'
    )


@router.delete('/{id}', response_model=schemas.Analytics)
async def delete_analytics(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    item = await crud.analytics.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Analytics not found')
    _assert_can_access(item, current_user)
    _unlink(item.html_path)
    _unlink(item.xlsx_path)
    item = await crud.analytics.delete(db=db, id=id)
    return item

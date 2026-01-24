from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

import crud, models, schemas  # noqa
from api import deps  # noqa


router = APIRouter()


@router.get('/device', response_model=List[schemas.OptionInt])
async def get_device_options(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve device options.
    """
    rows = await crud.device.get_rows(db)
    return JSONResponse([{
        'text': rows[i].name if rows[i].name else rows[i].ext_id,
        'value': rows[i].id
    } for i in range(len(rows))])


@router.get('/service', response_model=List[schemas.OptionInt])
async def get_service_option(
    *,
    db: Session = Depends(deps.get_db), alias: bool | None,
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve service options.
    """
    rows = await crud.service.get_rows(db)
    return JSONResponse([{
        'text': rows[i].name if rows[i].name else rows[i].alias,
        'value': rows[i].alias if alias else rows[i].id
    } for i in range(len(rows))])


@router.get('/proxy_group', response_model=List[schemas.OptionInt])
async def get_proxy_group_options(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve routing proxy options.
    """
    rows = await crud.proxy_group.get_rows(
        db, orders=[{'field': 'id', 'dir': 'desc'}]
    )
    return JSONResponse([{
        'text': rows[i].name,
        'value': rows[i].id
    } for i in range(len(rows))])


@router.get('/proxy', response_model=List[schemas.OptionInt])
async def get_proxy_options(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve routing proxy options.
    """
    rows = await crud.proxy.get_rows(db)
    return JSONResponse([{
        'text': rows[i].name if rows[i].name else rows[i].url,
        'value': rows[i].id
    } for i in range(len(rows))])


@router.get('/api_key', response_model=List[schemas.OptionStr])
async def get_api_key_options(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve api_key options.
    """
    api_keys = set()
    for key in await crud.report.get_api_keys(db):
        api_keys.add(key.api_key)
    for key in await crud.setting_group.get_api_keys(db):
        api_keys.add(key.api_key)

    return [{'text': api_key, 'value': api_key} for api_key in list(api_keys)]

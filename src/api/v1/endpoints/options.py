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
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve service options.
    """
    rows = await crud.service.get_rows(db)
    return JSONResponse([{
        'text': rows[i].name if rows[i].name else rows[i].alias,
        'value': rows[i].id
    } for i in range(len(rows))])


@router.get('/proxy', response_model=List[schemas.OptionInt])
async def get_peers_options(
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


@router.get('/api_key', response_model=List[schemas.OptionInt])
async def get_peers_options(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve api_key options.
    """
    rows = await crud.report.get_api_keys(db)
    return JSONResponse([{
        'text': rows[i].api_key,
        'value': rows[i].api_key
    } for i in range(len(rows))])

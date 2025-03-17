from datetime import datetime, timedelta
from typing import Any, List, Optional  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa
import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/codes/count')  # , response_model=schemas.WebhookResponse)
async def get_codes_count(
    device_id: str,
    period: str,
    db: AsyncSession = Depends(deps.get_db),
    _=Depends(deps.check_api_key)
) -> Any:
    """Get codes count by device_id for the period"""
    match period[-1].lower():
        case 's':
            ts = datetime.utcnow() - timedelta(seconds=int(period[:-1]))
        case 'm':
            ts = datetime.utcnow() - timedelta(minutes=int(period[:-1]))
        case 'h':
            ts = datetime.utcnow() - timedelta(hours=int(period[:-1]))
        case 'd':
            ts = datetime.utcnow() - timedelta(days=int(period[:-1]))
        case _:
            ts = datetime.utcnow() - timedelta(seconds=int(period[:-1]))
    filters = [
        {'field': 'device_ext_id', 'operator': 'eq', 'value': device_id},
        {'field': 'timestamp', 'operator': 'gte', 'value': ts},
    ]
    count = await crud.number.get_count(db=db, filters=filters)
    return {
        'device_id': device_id,
        'from': ts.strftime('%Y-%m-%d %H:%M:%S'),
        'count': count
    }

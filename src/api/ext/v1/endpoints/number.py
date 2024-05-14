from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/get', response_model=schemas.Number)
async def get_number(
    db: AsyncSession = Depends(deps.get_db),
    _=Depends(deps.check_api_key),
    filter: schemas.NumberFilter = Depends(),
    *, service: str, last_minutes: int | None = None
) -> Any:
    """
    Get number.
    """
    number = await crud.number.get_by_service(
        db=db, service=service, last_minutes=last_minutes,
        filter=filter.model_dump()
    )
    if not number:
        raise HTTPException(status_code=404, detail='Number not found')
    reg = await crud.reg.create(db=db, obj_in=schemas.RegCreate(
        number_id=number.id, service=service))
    if reg:
        number.regs.append(reg)
    return number

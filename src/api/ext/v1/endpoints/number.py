from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/get', response_model=List[schemas.Number])
async def get_number(
    db: AsyncSession = Depends(deps.get_db),
    _=Depends(deps.check_api_key),
    filter: schemas.NumberFilter = Depends(),
    *, last_minutes: int | None = None, limit: int | None = None
) -> Any:
    """
    Get number.
    """
    numbers = await crud.number.get_by_service(
        db=db, last_minutes=last_minutes, limit=limit,
        filter=filter.model_dump()
    )
    # if not number:
    #     raise HTTPException(status_code=404, detail='Number not found')
    # reg = await crud.reg.create(db=db, obj_in=schemas.RegCreate(
    #     number_id=number.id, service=service))
    # if reg:
    #     number.regs.append(reg)
    return jsonable_encoder(numbers)

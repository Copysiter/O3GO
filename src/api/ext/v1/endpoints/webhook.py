from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa

from api import deps  # noqa
from tasks import webhook_handler
import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/', response_model=schemas.WebhookResponse)
async def webhook(
    data: schemas.WebhookRequest = Depends(),
    _=Depends(deps.check_api_key)
) -> Any:
    r = webhook_handler.delay(data.model_dump())
    return {'task_id': r.task_id}

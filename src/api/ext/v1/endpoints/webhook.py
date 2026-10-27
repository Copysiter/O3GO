from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa

from api import deps  # noqa
from tasks import webhook_handler
from core.logger import logger, E
import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/', response_model=schemas.WebhookResponse)
async def webhook(
    data: schemas.WebhookRequest = Depends(),
    _=Depends(deps.check_api_key)
) -> Any:
    try:
        r = webhook_handler.delay(data.model_dump())
    except Exception as error:
        logger.exception(event=E.TASK.PUBLISH.ERROR, extra={
            'task_name': 'webhook',
            'error': {'type': type(error).__name__, 'msg': str(error)},
        })
        raise
    logger.info(event=E.TASK.PUBLISH.SUCCESS, extra={
        'task_name': 'webhook', 'task_id': r.task_id,
    })
    return {'task_id': r.task_id}

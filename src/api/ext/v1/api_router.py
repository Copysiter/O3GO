from fastapi import APIRouter

from .endpoints import webhook, number  # noqa


api_router = APIRouter()

api_router.include_router(webhook.router, prefix='/webhook', tags=['Webhook'])
api_router.include_router(number.router, prefix='/numbers', tags=['Get Number'])

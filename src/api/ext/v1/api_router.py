from fastapi import APIRouter

from .endpoints import webhook, number, settings, stats  # noqa


api_router = APIRouter()

api_router.include_router(webhook.router, prefix='/webhook', tags=['Webhook'])
api_router.include_router(settings.router, prefix='/settings', tags=['Settings'])
api_router.include_router(number.router, prefix='/numbers', tags=['Get Numbers'])
api_router.include_router(stats.router, prefix='/stats', tags=['Stats'])

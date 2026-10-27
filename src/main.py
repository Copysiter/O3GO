import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from core.logger import logger, E
from core.config import settings

from db.init_db import init_db
from api.v1.api_router import api_router
from api.ext.v1.api_router import api_router as ext_api_router
from middlewares.stats import StatsMiddleware


def init_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(event=E.SYSTEM.APP.STARTUP)
        try:
            await init_db()
        except Exception as error:
            logger.exception(event=E.SYSTEM.APP.ERROR, extra={
                'error': {'type': type(error).__name__, 'msg': str(error)},
            })
            raise
        logger.info(event=E.SYSTEM.APP.SUCCESS)
        try:
            yield
        finally:
            logger.info(event=E.SYSTEM.APP.SHUTDOWN)

    app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f'{settings.API_VERSION_PREFIX}/docs',
        redoc_url=f'{settings.API_VERSION_PREFIX}/redoc',
        openapi_url=f'{settings.API_VERSION_PREFIX}/openapi.json',
        default_response_class=ORJSONResponse,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    if settings.STATS_ENABLE:
        app.add_middleware(
            StatsMiddleware,
            prefix=settings.STATS_PREFIX,
            host=settings.STATS_SERVER_HOST,
            port=settings.STATS_SERVER_PORT,
            block_urls=settings.STATS_BLOCK_URLS
        )

    app.include_router(api_router, prefix=settings.API_VERSION_PREFIX)

    ext_api = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f'{settings.EXT_API_VERSION_PREFIX}/docs',
        redoc_url=f'{settings.EXT_API_VERSION_PREFIX}/redoc',
        openapi_url=f'{settings.EXT_API_VERSION_PREFIX}/openapi.json',
        default_response_class=ORJSONResponse
    )

    ext_api.include_router(ext_api_router, prefix=settings.EXT_API_VERSION_PREFIX)

    app.mount('', ext_api)

    app.secret_key = settings.SECRET_KEY

    return app


app = init_app()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.PROJECT_HOST, port=settings.PROJECT_PORT,
        workers=settings.ASGI_WORKERS, log_config=None,
        access_log=False, reload=False
    )

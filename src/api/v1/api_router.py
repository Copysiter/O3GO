from fastapi import APIRouter

from .endpoints import base, auth, users, devices, services, proxies, report, numbers, options, utils  # noqa


api_router = APIRouter()

api_router.include_router(base.router, prefix='', tags=['Info'])
api_router.include_router(utils.router, prefix='/utils', tags=['Utils'])
api_router.include_router(auth.router, prefix='/auth', tags=['Auth'])
api_router.include_router(users.router, prefix='/users', tags=['Users'])
api_router.include_router(devices.router, prefix='/devices', tags=['Devices'])
api_router.include_router(services.router, prefix='/services', tags=['Services'])  # noqa
api_router.include_router(proxies.router, prefix='/proxies', tags=['Proxies'])
api_router.include_router(report.router, prefix='/report', tags=['Report'])
api_router.include_router(numbers.router, prefix='/numbers', tags=['Numbers'])
api_router.include_router(options.router, prefix='/options', tags=['Options'])

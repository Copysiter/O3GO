import time
import asyncio

from datetime import date
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.session import async_session

import models
import schemas
import crud


celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery.conf.broker_connection_retry_on_startup = True


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


async def get_device(db: AsyncSession, data: dict) -> models.Device:
    device = await crud.device.get_by_ext_id(
        db, ext_id=data.get('device_id')
    )
    if not device:
        device = await crud.device.create(db, obj_in={
            'ext_id': data.get('device_id')
        })

    obj_in = {}
    if data.get('root') is not None:
        obj_in['root'] = data.get('root')
    if data.get('operator') is not None:
        obj_in['operator'] = data.get('operator')

    device = await crud.device.update(db=db, db_obj=device, obj_in=obj_in)

    return device


async def get_service(db: AsyncSession, data: dict) -> models.Service:
    service = await crud.service.get_by_alias(
        db, alias=data.get('service')
    )
    if not service:
        service = await crud.service.create(db, obj_in={
            'alias': data.get('service')
        })
    return service


async def get_report(db: AsyncSession, data: dict) -> models.Report:
    today = date.today()
    api_key = data.get('api_key')
    device = data.get('device')
    service = data.get('service')
    status = data.get('status')
    if device and service:
        report = await crud.report.get_by(
            db=db, api_key=api_key, device_id=device.id,
            service_id=service.id, date=today
        )
        if not report:
            report = await crud.report.create(db, obj_in={
                'api_key': api_key,
                'device_id': device.id,
                'service_id': service.id
            })
        report = await crud.report.update(
            db=db, db_obj=report, obj_in={
                f'{status}_count': getattr(report, f'{status}_count') + 1
            }
        )
        return report


async def get_proxy(db: AsyncSession, data: dict) -> models.Proxy:
    proxy = await crud.proxy.get_by_url(
        db, url=data.get('proxy')
    )
    if not proxy:
        proxy = await crud.proxy.create(db, obj_in={
            'url': data.get('proxy')
        })
    if data.get('proxy_status') in ('good', 'bad'):
        proxy = await crud.proxy.update(
            db=db, db_obj=proxy, obj_in={
                f'{data.get("proxy_status")}_count': getattr(
                    proxy, f'{data.get("proxy_status")}_count') + 1
            }
        )
    return proxy


async def get_number(db, data):
    device = data.get('device')
    proxy = data.get('proxy')
    service = data.get('service')
    if proxy and service and device:
        number = await crud.number.get_by_number(
            db, number=data.get('number')
        )
        if not number:
            number = await crud.number.create(db=db, obj_in={
                'number': data.get('number'),
                'service_alias': service.alias,
                'api_key': data.get('api_key'),
                'proxy': proxy.url,
                'device_ext_id': device.ext_id,
                'info_1': data.get('info_1'),
                'info_2': data.get('info_2'),
                'info_3': data.get('info_3')
            })
        return number


async def event_handler(data: schemas.WebhookRequest):
    async with async_session() as db:
        if data.get('device_id'):
            data['device'] = await get_device(db, data)

        if data.get('status') in (
                'start', 'number', 'bad', 'code', 'no_code'):
            data['service'] = await get_service(db, data)

            if data.get('device') and data.get('service'):
                report = await get_report(db, data)

        if data.get('proxy'):
            data['proxy'] = await get_proxy(db, data)

        if data.get('number'):
            number = await get_number(db, data)


@celery.task(name="webhook")
def webhook_handler(data: schemas.WebhookRequest):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(event_handler(data))

import openpyxl

from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime, timedelta
from io import BytesIO

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/proxies')
async def export_proxies(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if crud.user.is_superuser(current_user):
        proxies = await crud.proxy.get_all(db=db, filters=filters)
    else:
        proxies = await crud.proxy.get_all_by_user(db=db, filters=filters)

    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Proxies'

    headers = [
        '№', 'Name', 'URL', 'APIKey', 'Good', 'Bad',
        'Last used', 'Last used successful'
    ]
    sheet.append(headers)

    for proxy in proxies:
        sheet.append([
            proxy.id,
            proxy.name,
            proxy.url,
            proxy.good_count,
            proxy.bad_count,
            proxy.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if proxy.timestamp else '',
            proxy.ts_1.strftime('%Y-%m-%d %H:%M:%S')
            if proxy.ts_1 else '',
        ])

    table_ref = 'A1:{}'.format(
        sheet.cell(row=sheet.max_row, column=sheet.max_column).coordinate
    )
    table = Table(displayName='DataTable', ref=table_ref)
    style = TableStyleInfo(
        name='TableStyleMedium9',
        showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False
    )
    table.tableStyleInfo = style
    sheet.add_table(table)

    for column in sheet.columns:
        adjusted_width = max(len(str(cell.value)) for cell in column)
        sheet.column_dimensions[
            column[0].column_letter].width = adjusted_width + 5

    workbook.save(output)
    output.seek(0)

    filename = f'o3go_stats_proxies_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.xlsx'
    headers = {
        'Content-Disposition': f'attachment; filename={filename}'
    }

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-'
                   'officedocument.spreadsheetml.sheet',
        headers=headers
    )


@router.get('/numbers')
async def export_numbers(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if crud.user.is_superuser(current_user):
        numbers = await crud.number.get_all(db=db, filters=filters)
    else:
        numbers = await crud.number.get_all_by_user(db=db, filters=filters)

    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Numbers'

    headers = [
        '№', 'Number', 'Service', 'APIKey', 'Device ID', 'Proxy',
        'Timestamp', 'Info_1', 'Info_2', 'Info_3'
    ]
    sheet.append(headers)

    for number in numbers:
        sheet.append([
            number.id,
            number.number,
            number.api_key,
            number.service_alias,
            number.device_ext_id,
            number.proxy,
            number.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if number.timestamp else '',
            number.info_1,
            number.info_2,
            number.info_3
        ])

    table_ref = 'A1:{}'.format(
        sheet.cell(row=sheet.max_row, column=sheet.max_column).coordinate
    )
    table = Table(displayName='DataTable', ref=table_ref)
    style = TableStyleInfo(
        name='TableStyleMedium9',
        showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False
    )
    table.tableStyleInfo = style
    sheet.add_table(table)

    for column in sheet.columns:
        adjusted_width = max(len(str(cell.value)) for cell in column)
        sheet.column_dimensions[
            column[0].column_letter].width = adjusted_width + 5

    workbook.save(output)
    output.seek(0)

    filename = f'o3go_stats_numbers_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.xlsx'
    headers = {
        'Content-Disposition': f'attachment; filename={filename}'
    }

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-'
                   'officedocument.spreadsheetml.sheet',
        headers=headers
    )


@router.get('/report')
async def export_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    COLUMN_NAMES_MAP = {
        'api_key': 'API Key',
        'device_id': 'Device ID',
        'device_name': 'Device Name',
        'device_ext_id': 'Ext ID',
        'device_operator': 'Operator',
        'device_root': 'Root',
        'timestamp': 'Timestamp',
        'timedelta': 'Timedelta',
        'ts_1': 'Last Success Code',
        'info_1': 'Info 1',
        'info_2': 'Info 2',
        'info_3': 'Info 3'
    }
    services = await crud.service.get_all(db=db)
    cost_map = {}
    service_map = {}
    for s in services:
        cost_map[s.id] = {'cost_1': s.cost_1 or 0, 'cost_2': s.cost_2 or 0}
        display_name = s.name or (s.alias or '').title()
        key_name = display_name.replace(' ', '_')
        service_map[s.id] = {'key': key_name, 'display': display_name}
    count_columns = [
        'start_count', 'number_count', 'code_count', 'no_code_count',
        'waiting_count', 'bad_count', 'error_1_count', 'error_2_count',
        'account_count', 'account_ban_count', 'sent_count', 'delivered_count',
    ]
    svc_keys = []
    for svc_id, svc_info in service_map.items():
        svc_key = svc_info['key']
        for c in count_columns:
            svc_keys.append(f'{svc_key}_{c}')
        for suffix, label in [
            ('code_cost', 'Code Cost'), ('code_total', 'Code Total'),
            ('sent_cost', 'Sent Cost'), ('sent_total', 'Sent Total'),
        ]:
            field = f'{svc_key}_{suffix}'
            svc_keys.append(field)
            COLUMN_NAMES_MAP[field] = f'{svc_info["display"]} {label}'
    COLUMN_NAMES_MAP['code_total'] = 'Total Code Cost'
    COLUMN_NAMES_MAP['sent_total'] = 'Total Sent Cost'
    all_keys = [
        'api_key', 'device_id', 'device_name', 'device_ext_id',
        'device_operator', 'device_root',
    ] + svc_keys + [
        'code_total', 'sent_total',
        'timestamp', 'timedelta', 'ts_1', 'info_1', 'info_2', 'info_3'
    ]
    if crud.user.is_superuser(current_user):
        reports = await crud.report.get_all(db=db, filters=filters)
    else:
        reports = await crud.report.get_all_by_user(db=db, filters=filters)
    for report in reports:
        code_total = 0
        sent_total = 0
        for svc_id, svc_info in service_map.items():
            svc_key = svc_info['key']
            costs = cost_map.get(svc_id, {'cost_1': 0, 'cost_2': 0})
            code_count = report.get(f'{svc_key}_code_count', 0) or 0
            sent_count = report.get(f'{svc_key}_sent_count', 0) or 0
            report[f'{svc_key}_code_cost'] = costs['cost_1']
            report[f'{svc_key}_code_total'] = round(costs['cost_1'] * code_count, 2)
            report[f'{svc_key}_sent_cost'] = costs['cost_2']
            report[f'{svc_key}_sent_total'] = round(costs['cost_2'] * sent_count, 2)
            code_total += costs['cost_1'] * code_count
            sent_total += costs['cost_2'] * sent_count
        report['code_total'] = round(code_total, 2)
        report['sent_total'] = round(sent_total, 2)
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Report'
    headers = [COLUMN_NAMES_MAP.get(k, k.replace('_', ' ').title()) for k in all_keys]
    sheet.append(headers)
    for report in reports:
        if report.get('timestamp'):
            report['timestamp'] = report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        if report.get('ts_1'):
            report['ts_1'] = report['ts_1'].strftime('%Y-%m-%d %H:%M:%S')
        sheet.append([report.get(k, 0) for k in all_keys])
    table_ref = 'A1:{}'.format(
        sheet.cell(row=sheet.max_row, column=sheet.max_column).coordinate
    )
    table = Table(displayName='DataTable', ref=table_ref)
    style = TableStyleInfo(
        name='TableStyleMedium9',
        showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False
    )
    table.tableStyleInfo = style
    sheet.add_table(table)
    for column in sheet.columns:
        adjusted_width = max(len(str(cell.value)) for cell in column)
        sheet.column_dimensions[
            column[0].column_letter].width = adjusted_width + 5
    workbook.save(output)
    output.seek(0)
    filename = f'o3go_stats_report_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.xlsx'
    headers = {
        'Content-Disposition': f'attachment; filename={filename}'
    }
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-'
                   'officedocument.spreadsheetml.sheet',
        headers=headers
    )

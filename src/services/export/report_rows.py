from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models


async def build_report_rows(
    db: AsyncSession, *, filters: list | None, current_user: models.User
) -> tuple[list[dict[str, Any]], list[models.Service]]:
    services = await crud.service.get_all(db=db)

    if crud.user.is_superuser(current_user):
        reports = await crud.report.get_all(db=db, filters=filters or [])
    else:
        reports = await crud.report.get_all_by_user(
            db=db, filters=filters or [], user=current_user
        )

    costs = {}
    for svc in services:
        svc_key = (svc.name or svc.alias.title()).replace(' ', '_')
        costs[svc_key] = {
            'cost_1': svc.cost_1 or 0,
            'cost_2': svc.cost_2 or 0,
        }

    for report in reports:
        code_total = 0
        sent_total = 0
        for svc_key, svc_costs in costs.items():
            code_count = report.get(f'{svc_key}_code_count', 0) or 0
            sent_count = report.get(f'{svc_key}_sent_count', 0) or 0
            report[f'{svc_key}_code_cost'] = svc_costs['cost_1']
            report[f'{svc_key}_code_total'] = round(
                svc_costs['cost_1'] * code_count, 2
            )
            report[f'{svc_key}_sent_cost'] = svc_costs['cost_2']
            report[f'{svc_key}_sent_total'] = round(
                svc_costs['cost_2'] * sent_count, 2
            )
            code_total += svc_costs['cost_1'] * code_count
            sent_total += svc_costs['cost_2'] * sent_count
        report['code_total'] = round(code_total, 2)
        report['sent_total'] = round(sent_total, 2)

    return reports, services

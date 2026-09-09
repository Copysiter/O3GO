from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models


def calculate_report_metric(
    report: dict[str, Any], service_key: str, metric: str
) -> float | None:
    if metric == 'code_pct':
        number = report.get(f'{service_key}_number_count', 0) or 0
        code = report.get(f'{service_key}_code_count', 0) or 0
        return round(code / number * 100, 1) if number else 0
    if metric == 'sent_avg':
        sent = report.get(f'{service_key}_sent_count', 0) or 0
        account = report.get(f'{service_key}_account_count', 0) or 0
        return round(sent / account, 1) if account else 0
    if metric == 'delivered_pct':
        delivered = report.get(f'{service_key}_delivered_count', 0) or 0
        sent = report.get(f'{service_key}_sent_count', 0) or 0
        return round(delivered / sent * 100, 1) if sent else 0
    return None


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
            'has_account_profit': 'account_profit' in (svc.columns or []),
        }

    for report in reports:
        account_profit = 0
        message_profit = 0
        for svc_key, svc_costs in costs.items():
            account_count = report.get(f'{svc_key}_account_count', 0) or 0
            sent_count = report.get(f'{svc_key}_sent_count', 0) or 0
            report[f'{svc_key}_account_cost'] = svc_costs['cost_1']
            service_account_profit = (
                svc_costs['cost_1'] * account_count
                if svc_costs['has_account_profit'] else 0
            )
            report[f'{svc_key}_account_profit'] = round(
                service_account_profit, 2
            )
            report[f'{svc_key}_message_cost'] = svc_costs['cost_2']
            report[f'{svc_key}_message_profit'] = round(
                svc_costs['cost_2'] * sent_count, 2
            )
            account_profit += service_account_profit
            message_profit += svc_costs['cost_2'] * sent_count
        report['account_profit'] = round(account_profit, 2)
        report['message_profit'] = round(message_profit, 2)

    return reports, services

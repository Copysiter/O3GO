from datetime import datetime
from pathlib import Path
from typing import Any

from services.export import analyze_reports as report_module


COUNTER_LABELS = {
    'start': 'Start Count',
    'number': 'Number Count',
    'code': 'Code Count',
    'no_code': 'No Code Count',
    'waiting': 'Waiting Count',
    'bad': 'Bad Count',
    'error_1': 'Error 1 Count',
    'error_2': 'Error 2 Count',
    'account': 'Account Count',
    'account_ban': 'Account Ban Count',
    'sent': 'Sent Count',
    'delivered': 'Delivered Count',
}

MONEY_LABELS = {
    'code_cost': 'Code Cost',
    'code_total': 'Code Total',
    'sent_cost': 'Sent Cost',
    'sent_total': 'Sent Total',
}


def _service_key(service: Any) -> str:
    return (service.name or service.alias.title()).replace(' ', '_')


def _service_display(service: Any) -> str:
    name = service.name or service.alias or 'Service'
    return name.replace('_', ' ').title()


def _money_prefixes(service: Any, svc_key: str, display_name: str) -> set[str]:
    prefixes = {svc_key, display_name}
    if service.alias:
        prefixes.add(service.alias)
        prefixes.add(service.alias.lower())
        prefixes.add(service.alias.title())
    if service.name:
        prefixes.add(service.name)
        prefixes.add(service.name.lower())
    return {p for p in prefixes if p}


def _build_dataframe(rows: list[dict[str, Any]], services: list[Any], report_module):
    pd = report_module.pd
    records = []
    config_path = Path('/storage/employees.yml')
    config = report_module.load_employee_config(config_path) if config_path.exists() else None
    key_to_emp = config['key_to_emp'] if config else {}

    for row in rows:
        api_key = row.get('api_key') or ''
        record = {
            'API Key': api_key,
            'Device': row.get('device_id'),
            'Ext ID': row.get('device_ext_id'),
            'Root': row.get('device_root'),
            'Operator': row.get('device_operator'),
            'Total Code Cost': row.get('code_total') or 0,
            'Total Sent Cost': row.get('sent_total') or 0,
            'Timestamp': row.get('timestamp'),
            'Last Activity': row.get('timestamp'),
            'Last Success Code': row.get('ts_1'),
            'Timedelta': (row.get('timedelta') or 0) / 3600,
            'Info 1': row.get('info_1'),
            'Info 2': row.get('info_2'),
            'Info 3': row.get('info_3'),
        }

        if key_to_emp:
            record['_norm_key'] = report_module.normalize_key(api_key)
            record['_Сотрудник'] = key_to_emp.get(record['_norm_key'], 'Неизвестно')
        else:
            record['_Сотрудник'] = api_key or 'Неизвестно'

        for service in services:
            svc_key = _service_key(service)
            display_name = _service_display(service)
            for short, label in COUNTER_LABELS.items():
                value = row.get(f'{svc_key}_{short}_count') or 0
                record[f'{display_name} {label}'] = value
            for short, label in MONEY_LABELS.items():
                value = row.get(f'{svc_key}_{short}') or 0
                record[f'{display_name} {label}'] = value
                for prefix in _money_prefixes(service, svc_key, display_name):
                    record[f'{prefix} {label}'] = value

        records.append(record)

    if not records:
        raise ValueError('No report rows found for selected filters')

    all_data = pd.DataFrame(records)
    employees = all_data['_Сотрудник'].dropna().unique().tolist()
    unmatched = sorted(
        all_data[all_data['_Сотрудник'] == 'Неизвестно']['API Key']
        .dropna().unique().tolist()
    ) if key_to_emp else []
    if config:
        employees_order = [e for e in config['all_employees'] if e in employees]
        if 'Неизвестно' in employees:
            employees_order.append('Неизвестно')
        mode_info = {
            'mode': 'config',
            'unmatched_keys': unmatched,
            'config': config,
        }
    else:
        employees_order = employees
        mode_info = {
            'mode': 'filename',
            'unmatched_keys': [],
            'config': None,
        }
    return all_data, employees_order, mode_info


def _period_info(all_data, report_module, fallback: str) -> str:
    if 'Timestamp' not in all_data.columns:
        return fallback or 'не определён'
    try:
        ts = report_module.pd.to_datetime(
            all_data['Timestamp'], errors='coerce'
        ).dropna()
    except Exception:
        return fallback or 'не определён'
    if len(ts):
        return f'{ts.min():%d.%m.%Y} — {ts.max():%d.%m.%Y}'
    return fallback or 'не определён'


def generate_analytics_files(
    *, analytics_id: int, period: str,
    rows: list[dict[str, Any]], services: list[Any]
) -> tuple[str, str, str, str]:
    all_data, employees, mode_info = _build_dataframe(rows, services, report_module)
    all_data = report_module.enrich(all_data)
    period_info = _period_info(all_data, report_module, period)

    summary = report_module.compute_summary(all_data)
    emp_totals = dict(zip(summary['Сотрудник'], summary['Итого_руб']))
    api_break = report_module.compute_api_breakdown(all_data, emp_totals)
    top_dev = report_module.compute_top_devices(all_data, n=30)
    model_stats = report_module.compute_model_stats(all_data)
    recs = report_module.build_recommendations(summary)
    svc_eff = report_module.compute_service_efficiency(all_data)
    checks = report_module.run_sanity_checks(all_data, summary, employees, mode_info)
    confidence = report_module.assess_confidence(checks, period_info, summary)

    out_dir = Path('/storage/analytics')
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f'analytics_{analytics_id}_{datetime.utcnow():%Y%m%d%H%M%S}'
    html_filename = f'{stem}.html'
    xlsx_filename = f'{stem}.xlsx'
    html_path = out_dir / html_filename
    xlsx_path = out_dir / xlsx_filename

    report_module.write_excel(
        summary, api_break, top_dev, model_stats, recs, period_info,
        checks, confidence, svc_eff, all_data, xlsx_path
    )
    report_module.write_html(
        summary, top_dev, recs, period_info, checks, confidence,
        svc_eff, all_data, html_path
    )
    return str(html_path), str(xlsx_path), html_filename, xlsx_filename

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from api import deps
from services.export import analyze_reports

import models


router = APIRouter()


@router.post('/employees/upload')
async def upload_employees_config(
    *,
    file: UploadFile,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    filename = file.filename or ''
    if not filename.endswith(('.yml', '.yaml')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .yml or .yaml files are allowed',
        )

    content = await file.read()
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File must be UTF-8 encoded',
        )

    storage_dir = Path('/storage')
    storage_dir.mkdir(parents=True, exist_ok=True)
    target_path = storage_dir / 'employees.yml'
    tmp_path = storage_dir / '.employees.yml.tmp'

    tmp_path.write_text(text, encoding='utf-8')
    try:
        config = analyze_reports.load_employee_config(tmp_path)
        if not config or not config.get('all_employees'):
            raise ValueError('employees config must contain at least one employee')
    except (Exception, SystemExit) as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid employees config: {exc}',
        )

    tmp_path.replace(target_path)
    return {
        'filename': target_path.name,
        'employees': len(config['all_employees']),
        'api_keys': len(config['key_to_emp']),
    }

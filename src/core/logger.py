"""Настройка логирования через неизменённый пакет atol_logging."""
from atol_logging import Config, Event, RequestIdFilter, setup_logger

from .config import settings


SERVICE_INFO = {
    'name': settings.PROJECT_NAME,
    'version': settings.PROJECT_VERSION,
    'env': settings.PROJECT_ENVIRONMENT,
    'instance_id': settings.PROJECT_INSTANCE_ID,
}

EVENT_MAP: Config = {
    'SYSTEM': (1, {
        'APP': (1, {
            'STARTUP': (1, 'Запуск приложения'),
            'SHUTDOWN': (2, 'Остановка приложения'),
            'SUCCESS': (3, 'Приложение успешно запущено'),
            'ERROR': (5, 'Ошибка приложения'),
        }),
        'API': (3, {
            'ERROR': (7, 'Ошибка при обработке запроса'),
        }),
    }),
    'AUTH': (2, {
        'LOGIN': (1, {
            'SUCCESS': (1, 'Успешная аутентификация'),
            'FAILURE': (4, 'Аутентификация не пройдена'),
        }),
        'ACCESS': (2, {
            'DENIED': (2, 'Доступ запрещён'),
        }),
    }),
    'DB': (3, {
        'CONNECTION': (1, {
            'INIT': (1, 'Инициализация БД'),
            'SUCCESS': (2, 'БД инициализирована'),
            'ERROR': (4, 'Ошибка инициализации БД'),
        }),
    }),
    'TASK': (9, {
        'EXECUTION': (1, {
            'START': (1, 'Начало выполнения задачи'),
            'SUCCESS': (2, 'Задача выполнена'),
            'ERROR': (3, 'Ошибка выполнения задачи'),
            'RETRY': (4, 'Повтор выполнения задачи'),
        }),
        'PUBLISH': (2, {
            'SUCCESS': (1, 'Задача опубликована'),
            'ERROR': (2, 'Ошибка публикации задачи'),
        }),
    }),
}

logger = setup_logger(
    name=settings.LOG_NAME,
    level=settings.LOG_LEVEL,
    log_path=settings.LOG_PATH,
    rotation_type=settings.LOG_ROTATION_TYPE,
    rotation_when=settings.LOG_ROTATION_WHEN,
    rotation_interval=settings.LOG_ROTATION_INTERVAL,
    backup_count=settings.LOG_BACKUP_COUNT,
    stdout=settings.LOG_STDOUT,
    enabled_loggers=settings.LOG_ENABLED_LOGGERS,
    service=SERVICE_INFO,
)

logger.addFilter(RequestIdFilter())

E = Event(EVENT_MAP)

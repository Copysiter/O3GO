import crud, schemas  # noqa
from core.config import settings  # noqa
from core.logger import logger, E
from db.base_class import Base  # noqa
from db.session import engine, async_session  # noqa


# Create first superuser
async def create_superuser() -> None:
    async with async_session() as session:
        try:
            user = await crud.user.get_by_login(
                session,
                login=settings.FIRST_SUPERUSER
            )
            if not user:
                user_in = schemas.UserCreate(
                    login=settings.FIRST_SUPERUSER,
                    name='Admin',
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_active=True,
                    is_superuser=True,
                )
                user = await crud.user.create(session, obj_in=user_in)
        except Exception as error:
            # Preserve the existing best-effort superuser initialization.
            logger.exception(event=E.DB.CONNECTION.ERROR, extra={
                'action': 'create_superuser',
                'error': {'type': type(error).__name__, 'msg': str(error)},
            })


# Create tables
async def init_models() -> None:
    async with engine.begin() as conn:
        if settings.DATABASE_DELETE_ALL:
            await conn.run_sync(Base.metadata.drop_all)
        if settings.DATABASE_CREATE_ALL:
            await conn.run_sync(Base.metadata.create_all)


async def init_db() -> None:
    logger.info(event=E.DB.CONNECTION.INIT)
    await init_models()
    logger.info(event=E.DB.CONNECTION.SUCCESS)
    await create_superuser()

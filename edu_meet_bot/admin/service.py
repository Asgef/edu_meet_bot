from edu_meet_bot.admin.errors import (
UserAlreadyAdmin, UserAlreadyIsNotAdmin, UserNeverBeenAdmin
)
from edu_meet_bot.admin.repo import (change_user_admin_status_by_id,
                                 get_user_by_tg_id, is_user_admin_by_tg_id)
from edu_meet_bot.db import async_session
from edu_meet_bot.errors import UserNotFoundError


async def is_user_admin(tg_id: int) -> bool:
    async with async_session() as session:
        # TODO: Реализовать кэширование
        result = await session.execute(is_user_admin_by_tg_id(tg_id))
        return result.scalar()  # type: ignore


async def make_user_admin(tg_id: int):
    async with async_session() as session:
        result = await session.execute(get_user_by_tg_id(tg_id))
        user = result.scalar_one_or_none()
        if user:
            if user.is_admin:
                raise UserAlreadyAdmin()

            await session.execute(change_user_admin_status_by_id(
                user.tg_id, True))
            await session.commit()
            return

        raise UserNotFoundError()


async def delete_user_from_admins(tg_id: int):
    async with async_session() as session:
        result = await session.execute(get_user_by_tg_id(tg_id))
        user = result.first()

        if not user:
            raise UserNeverBeenAdmin()

        if not user.is_admin:
            raise UserAlreadyIsNotAdmin()

        await session.execute(change_user_admin_status_by_id(user.id, False))

from edu_meet_bot.admin.errors import (
UserAlreadyAdmin, UserAlreadyIsNotAdmin, UserNeverBeenAdmin
)
from edu_meet_bot.session.models import User
from edu_meet_bot.admin.repo import (change_user_admin_status_by_id,
                                 get_user_by_tg_id, is_user_admin_by_tg_id)
from edu_meet_bot.db import async_session


async def is_user_admin(tg_id: int) -> bool:
    async with async_session() as session:
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
                user.id, True))
            return

        new_user = User(user_id=tg_id)
        session.add(new_user)
        await session.commit()


async def delete_user_from_admins(tg_id: int):
    async with async_session() as session:
        result = await session.execute(get_user_by_tg_id(tg_id))
        user = result.first()

        if not user:
            raise UserNeverBeenAdmin()

        if not user.is_admin:
            raise UserAlreadyIsNotAdmin()

        await session.execute(change_user_admin_status_by_id(user.id, False))

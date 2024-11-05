from datetime import datetime, timedelta, timezone
from edu_meet_bot.session.models import User
from edu_meet_bot.admin.repo import get_user_by_tg_id
from edu_meet_bot.db import async_session
from sqlalchemy.sql import func


async def touch_user(tg_id: int, username: str, first_name: str):
    async with async_session() as session:
        result = await session.execute(get_user_by_tg_id(tg_id))
        user = result.scalar_one_or_none()
        if not user:
            new_user = User(
                tg_id=tg_id, username=username, first_name=first_name
            )
            session.add(new_user)
            await session.commit()
            return
        #  TODO: Следует продумать логику обновления активности пользователя
        #  Возможно следует реагировать на некоторые события
        #  или если будет Redis использовать его
        current_time = datetime.now(timezone.utc)  # Текущее время в UTC
        if current_time - user.last_activity > timedelta(minutes=15):
            user.last_activity = func.now()
            await session.commit()

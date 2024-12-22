from datetime import datetime, timedelta, timezone
from edu_meet_bot.general_menu.models import User
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

        # Получаем текущее время и сравниваем с last_activity
        current_time = datetime.now(timezone.utc)
        last_activity = user.last_activity.replace(tzinfo=timezone.utc)\
            if user.last_activity.tzinfo is None\
            else user.last_activity

        # Проверяем, нужно ли обновлять last_activity
        if current_time - last_activity > timedelta(minutes=15):
            user.last_activity = func.now()  # Обновляем last_activity
            await session.commit()
            # Коммит только если last_activity обновляется

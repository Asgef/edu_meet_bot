from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from edu_meet_bot.admin.service import is_user_admin
from edu_meet_bot.general_menu.service import touch_user


class UserActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Обновляем активность пользователя
        await touch_user(
            event.from_user.id, event.from_user.username,
            event.from_user.first_name
        )
        # Проверяем статус администратора
        is_admin = await is_user_admin(event.from_user.id)
        data['is_admin'] = is_admin
        #  TODO: следует реализовать кэширование is_admin с помощью Redis
        # или объединить функции touch_user и is_user_admin что вроде как
        # нарушает некоторые принципы  Zen of Python.
        return await handler(event, data)

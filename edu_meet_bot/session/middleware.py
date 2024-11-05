from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from edu_meet_bot.session.service import touch_user



class UserActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        await touch_user(
            event.from_user.id, event.from_user.username,
            event.from_user.first_name
        )
        return await handler(event, data)

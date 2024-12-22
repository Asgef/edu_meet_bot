from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher
from edu_meet_bot.general_menu.routes import router as tutor_router
from edu_meet_bot.support.routes import router as support_router
from edu_meet_bot.registration.routes import router as registration_router
from edu_meet_bot.sessions.routes import router as sessions_router
from edu_meet_bot.general_menu.middleware import UserActivityMiddleware


async def start_bot() -> None:
    if settings.DEBUG:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - "
            "(%(filename)s:%(funcName)s:%(lineno)d) - %(message)s"

        )

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    dp.message.middleware(UserActivityMiddleware())
    dp.include_router(tutor_router)
    dp.include_router(support_router)
    dp.include_router(registration_router)
    dp.include_router(sessions_router)
    # удаляет вебхук бота и сбрасывает все ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

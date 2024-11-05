from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher
from edu_meet_bot.session.routes import router as tutor_router
from edu_meet_bot.session.middleware import UserActivityMiddleware


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
    # удаляет вебхук бота и сбрасывает все ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

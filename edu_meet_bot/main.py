from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher
from edu_meet_bot.session.router import router as tutor_router


async def start_bot() -> None:
    if settings.DEBUG:
        logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    dp.include_router(tutor_router)
    # удаляет вебхук бота и сбрасывает все ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

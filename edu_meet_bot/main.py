from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher


async def start_bot() -> None:
    if settings.DEBUG:
        logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    # удаляет вебхук бота и сбрасывает все ожидающие обновления
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

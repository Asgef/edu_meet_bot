from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher
from edu_meet_bot.general_menu.routes import router as tutor_router
from edu_meet_bot.support.routes import router as support_router
from edu_meet_bot.registration.routes import router as registration_router
from edu_meet_bot.sessions.routes import router as sessions_router
from edu_meet_bot.general_menu.middleware import UserActivityMiddleware
from edu_meet_bot.general_menu.routes import webhook_handler
import asyncio
from aiohttp import web


# Webhook
async def on_startup(bot: Bot, app: web.Application) -> None:
    if settings.PRODUCTION:
        await bot.set_webhook(
            f'https://{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}'
        )


async def on_shutdown(bot: Bot) -> None:
    if settings.PRODUCTION:
        await bot.delete_webhook()


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

    if settings.PRODUCTION:
        app = web.Application()
        app["bot"] = bot

        app.router.add_post(settings.WEBHOOK_PATH, webhook_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner, host="0.0.0.0", port=settings.WEBHOOK_PORT
        )
        await site.start()

        logging.info('>>>>>> Bot is running via webhook <<<<<<')
        await dp.start_polling(bot)  # Основной функционал бота
    else:
        # Локальная разработка: запуск через polling
        await dp.start_polling(bot)

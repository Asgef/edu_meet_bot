from edu_meet_bot import settings
import logging
from aiogram import Bot, Dispatcher
from edu_meet_bot.general_menu.routes import router as tutor_router
from edu_meet_bot.support.routes import router as support_router
from edu_meet_bot.sessions.routes import router as sessions_router
from edu_meet_bot.registration.routes import router as registration_router
from edu_meet_bot.general_menu.middleware import UserActivityMiddleware
from edu_meet_bot.general_menu.routes import web_router
import asyncio
from aiohttp import web


# Notify
async def start_http_server(bot: Bot) -> None:
    logging.info(">>>>>>>>>>>>>> Starting http server")
    app = web.Application()
    app.add_routes(web_router)
    app['bot'] = bot
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", settings.NOTIFICATION_PORT)
    await site.start()
    logging.info(
        f'>>>>>> HTTP server is running on http://127.0.0.1:'
        f'{settings.NOTIFICATION_PORT} <<<<<<'
    )


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
        await asyncio.gather(
            start_http_server(bot),
            dp.start_polling(bot)
        )
    else:
        # Локальная разработка: запуск через polling
        await dp.start_polling(bot)

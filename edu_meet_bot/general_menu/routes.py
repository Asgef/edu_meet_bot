import logging
import os.path
from edu_meet_bot import settings
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, User, FSInputFile, ContentType
from edu_meet_bot.general_menu.keyboard import main_menu_view
from aiohttp import web


router = Router(name="edu_meet_bot")
web_router  = web.RouteTableDef()


@router.message(CommandStart())
async def start(message: Message, is_admin: bool) -> None:
    user: User = message.from_user
    logging.info(user)

    await message.answer(
        "Привет! Я бот для планирования уроков с репетитором. "
        "Отправьте / help, чтобы увидеть мои команды.",
        reply_markup=main_menu_view(is_admin)
    )


@router.message(Command("help"))
async def help(message: Message) -> None:
    await message.answer("Мои команды: /start, /help")


# @router.message(F.text == "Записаться")
# async def registration_menu(message: Message, bot=Bot):
#     await message.answer("Заходи", reply_markup=lesson_registration_menu())


@router.message(F.text == "О Нике")
async def get_about_massage(message: Message, bot=Bot):
    photo_file: str = os.path.join(
        str(settings.MEDIA_ROOT), str(settings.TUTOR_PHOTO)
    )
    caption = settings.ABOUT_MASSAGE
    await message.answer_photo(FSInputFile(photo_file), caption=caption)


# @router.message()
# async def tutor_message(message: Message) -> None:
#     if message.text and re.search(
#             r'(егэ|математик|информатик)', message.text, re.IGNORECASE
#     ):
#         await message.answer(
#           "Я помогу тебе к ЕГЭ по математике и информатике"
#         )

@web_router.post(settings.NOTIFICATION_PATH)
async def notify_handler(request: web.Request):
    bot: Bot = request.app['bot']
    data = await request.json()
    user_tg_id = data.get("tg_id")
    message = data.get("message")

    if user_tg_id and message:
        await bot.send_message(user_tg_id, message)
        return web.json_response({"status": "ok"}, status=200)
    return web.json_response(
        {"status": "error", "message": "Invalid data"}, status=400
    )



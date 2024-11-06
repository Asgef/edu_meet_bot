import logging
import os.path

from edu_meet_bot import settings
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, User, FSInputFile
import re
from edu_meet_bot.session.views import main_menu_view, lesson_registration_menu

router = Router(name="edu_meet_bot")


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


@router.message(F.text == "Записаться")
async def registration_menu(message: Message, bot=Bot):
    await message.answer("Заходи", reply_markup=lesson_registration_menu())


@router.message(F.text == "О Нике")
async def get_about_massage(message: Message, bot=Bot):
    photo_file: str = os.path.join(
        str(settings.MEDIA_ROOT), str(settings.TUTOR_PHOTO)
    )
    caption = settings.ABOUT_MASSAGE
    await message.answer_photo(FSInputFile(photo_file), caption=caption)


@router.message()
async def tutor_message(message: Message) -> None:
    if message.text and re.search(
            r'(егэ|математик|информатик)', message.text, re.IGNORECASE
    ):
        await message.answer("Я помогу тебе к ЕГЭ по математике и информатике")

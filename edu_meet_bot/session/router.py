from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import re
from edu_meet_bot.session.views import main_menu_view


router = Router(name="edu_meet_bot")


@router.message(CommandStart())
async def start(message: Message) -> None:

    await message.answer(
        "Привет! Я бот для планирования уроков с репетитором. "
        "Отправьте / help, чтобы увидеть мои команды.",
        reply_markup=main_menu_view(),
    )


@router.message(Command("help"))
async def help(message: Message) -> None:
    await message.answer("Мои команды: /start, /help")


@router.message()
async def tutor_message(message: Message) -> None:
    if re.search(r'(егэ|математик|информатик)', message.text, re.IGNORECASE):
        await message.answer("Я помогу тебе к ЕГЭ по математике и информатике")

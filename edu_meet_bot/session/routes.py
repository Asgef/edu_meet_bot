from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import re
from edu_meet_bot.session.views import main_menu_view, lesson_registration_menu
import json

router = Router(name="edu_meet_bot")


@router.message(CommandStart())
async def start(message: Message) -> None:

    await message.answer(
        "Привет! Я бот для планирования уроков с репетитором. "
        "Отправьте / help, чтобы увидеть мои команды.",
        reply_markup=main_menu_view()
    )


@router.message(Command("help"))
async def help(message: Message) -> None:
    await message.answer("Мои команды: /start, /help")


@router.message(F.text == "Записаться")
async def registration_menu(message: Message, bot=Bot):
    await message.answer("Заходи", reply_markup=lesson_registration_menu())
    # json_str = json.dumps(message.dict(), default=str)
    # print(json_str)


@router.message()
async def tutor_message(message: Message) -> None:
    if re.search(r'(егэ|математик|информатик)', message.text, re.IGNORECASE):
        await message.answer("Я помогу тебе к ЕГЭ по математике и информатике")

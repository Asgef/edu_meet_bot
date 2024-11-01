from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def main_menu_view():
    kb = ReplyKeyboardBuilder()

    kb.add(KeyboardButton(text='Записаться на занятие'))
    kb.add(KeyboardButton(text='О Нике'))
    kb.add(KeyboardButton(text='Задать Нике вопрос'))
    kb.add(KeyboardButton(text='Мои сессии'))

    kb.adjust(1, 3)

    return kb.as_markup(resize_keyboard=True)

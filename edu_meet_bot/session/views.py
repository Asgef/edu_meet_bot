from gc import callbacks

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton


def main_menu_view():
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="Записаться"))
    kb.add(KeyboardButton(text="Мои занятия"))
    kb.add(KeyboardButton(text="О Нике"))
    kb.add(KeyboardButton(text="Задать Нике вопрос"))

    kb.adjust(1, 3)
    return kb.as_markup(resize_keyboard=True)


def lesson_registration_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text='Математика', callback_data='math')
    kb.button(text='Информатика', callback_data='info')

    kb.adjust(2)
    return kb.as_markup()
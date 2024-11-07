from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_view(is_admin: bool = False):
    kb = ReplyKeyboardBuilder()
    # kb.add(KeyboardButton(text="Записаться"))
    # kb.add(KeyboardButton(text="Мои занятия"))
    kb.button(text="О Нике")
    kb.add(KeyboardButton(text="Связаться с репетитором"))

    if is_admin:
        kb.button(text="Админ панель")

    kb.adjust(1, 3)
    return kb.as_markup(resize_keyboard=True)


# def lesson_registration_menu():
#     kb = InlineKeyboardBuilder()
#     kb.button(text='Математика', callback_data='math')
#     kb.button(text='Информатика', callback_data='info')
#
#     kb.adjust(2)
#     return kb.as_markup()

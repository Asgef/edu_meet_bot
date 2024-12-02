from aiogram.utils.keyboard import InlineKeyboardBuilder


def select_date(user_id: int, user_name):
    kb = InlineKeyboardBuilder()
    kb.button(text="Выбрать дату", callback_data=f"select_date|{user_id}|{user_name}")
    return kb.as_markup()

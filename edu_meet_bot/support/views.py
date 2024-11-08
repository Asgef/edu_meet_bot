from aiogram.utils.keyboard import InlineKeyboardBuilder


def answer_button(user_id: int, user_name):
    kb = InlineKeyboardBuilder()
    kb.button(text="Ответить", callback_data=f"answer|{user_id}|{user_name}")
    return kb.as_markup()

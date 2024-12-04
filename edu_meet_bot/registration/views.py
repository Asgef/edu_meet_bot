from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Callable
from datetime import date
from edu_meet_bot.session.models import Slot


def select_date(user_id: int, user_name):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Выбрать дату", callback_data=f"select_date|{user_id}|{user_name}"
    )
    return kb.as_markup()


def select_week(
        period: Dict[date, List[Slot]],
        label_func: Callable[[date, date], str],
        callback_prefix: str
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for period_start, slots in sorted(period.items()):
        # Определяем последнюю дату слота в группе
        last_slot_date = max(slot.date for slot in slots)

        # Формируем метку для кнопки
        period_label = label_func(period_start, last_slot_date)

        # Добавляем кнопку в клавиатуру
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=period_label,
                callback_data=f"{callback_prefix}|"
                              f"{period_start.isoformat()}|"
                              f"{last_slot_date.isoformat()}"
            )
        ])

    return keyboard


def select_day(
    period: Dict[date, List[Slot]],
    label_func: Callable[[date], str],
    callback_prefix: str
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for period_start in sorted(period.keys()):
        period_label = label_func(period_start)
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=period_label,
                callback_data=f"{callback_prefix}|{period_start.isoformat()}"
            )
        ])
    return keyboard


def select_slot(
        slots: List[Slot],
        label_func: Callable[[Slot], str],
        callback_prefix: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for slot in slots:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=label_func(slot),
                callback_data=f"{callback_prefix}|{slot.id}"
            )
        ])
    return keyboard

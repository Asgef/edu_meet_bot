import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Callable
from datetime import date
from edu_meet_bot.general_menu.models import Order, Slot, AcademicSubject


def select_session(
    sessions: Dict[date, List[Order]],
):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    pass
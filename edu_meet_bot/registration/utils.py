from edu_meet_bot.session.models import Slot, SlotStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from sqlalchemy import select
from typing import Dict, List, Callable
from functools import wraps
import traceback
import logging
import inspect


async def get_available_slots(db_session: AsyncSession, start_date: date, end_date: date = None) -> List[Slot]:
    """Get available slots for a specified period."""
    if end_date is None:
        end_date = start_date + timedelta(days=365)  # или другое значение по умолчанию
    query = select(Slot).where(
        Slot.date >= start_date,
        Slot.date <= end_date,
        Slot.status == SlotStatus.AVAILABLE.value
    )
    result = await db_session.execute(query)
    return result.scalars().all()


def group_slots_by_time_period(slots: List[Slot], period: str, today: date = None) -> Dict[date, List[Slot]]:
    """Группировка слотов по указанному периоду (день, неделя)."""

    if period == "day":
        key_func: Callable[[Slot], date] = lambda slot: slot.date.date()

    elif period == "week":
        def key_func(slot: Slot) -> date:
            # Начало недели с учетом ограничения на today
            period_start = slot.date.date() - timedelta(days=slot.date.weekday())
            return max(period_start, today)

    else:
        raise ValueError(f"Unsupported period: {period}. Use 'day' or 'week'.")

    grouped_slots = {}
    for slot in slots:
        period_start = key_func(slot)
        grouped_slots.setdefault(period_start, []).append(slot)

    return grouped_slots



def create_week_selection_keyboard(
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
                callback_data=f"{callback_prefix}|{period_start.isoformat()}"
            )
        ])

    return keyboard

def create_day_selection_keyboard(
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


def create_time_selection_keyboard(slots: List[Slot], label_func: Callable[[Slot], str], callback_prefix: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for slot in slots:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=label_func(slot),
                callback_data=f"{callback_prefix}|{slot.id}"
            )
        ])
    return keyboard


async def handle_no_slots(message, period_desc: str):
    await message.answer(f"Нет доступных слотов на выбранный {period_desc}.")


from functools import wraps

def handle_exceptions(func):
    """Декоратор для обработки исключений."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            logging.error(traceback.format_exc())
            if "callback" in kwargs:
                await kwargs["callback"].message.answer(
                    "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
                )
            elif args:
                await args[0].message.answer(
                    "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
                )
            return None
    return wrapper


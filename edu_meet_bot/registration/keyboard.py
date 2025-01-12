import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Callable
from datetime import date
from edu_meet_bot.general_menu.models import Slot, AcademicSubject


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

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_subjects"
        )
    ])

    return keyboard


def select_day(
    period: Dict[date, List[Slot]],
    label_func: Callable[[date], str],
    callback_prefix: str,
    week_start,
    week_end
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for period_start in sorted(period.keys()):
        period_label = label_func(period_start)
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=period_label,
                callback_data=(
                    f"{callback_prefix}|{period_start.isoformat()}|"
                    f"{week_start}|{week_end}"
                )
            )
        ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="select_date|"
        )
    ])
    return keyboard


def select_slot(
        slots: List[Slot],
        label_func: Callable[[Slot], str],
        callback_prefix: str,
        week_start,
        week_end

) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for slot in slots:
        logging.info(f'slot >>>>>>>>>>>: {slot}')
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=label_func(slot),
                callback_data=f"{callback_prefix}|{slot.id}|"
                              f"{slot.time_start.strftime('%H:%M')}|"
                              f"{slot.date.isoformat()}"
            )
        ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"select_week|{week_start}|{week_end}"
        )
    ])
    return keyboard


def academic_subject_button(
        subjects: List[AcademicSubject]
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"📚 {sub.name}",
                callback_data=f"select_date|{sub.id}|{sub.name}"
            )]
            for sub in subjects
        ]
    )

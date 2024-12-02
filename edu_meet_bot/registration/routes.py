from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.registration.views import select_date
from datetime import datetime, timedelta
from edu_meet_bot.db import async_session
import logging
import traceback
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period,
    create_period_selection_keyboard, handle_no_slots, handle_exceptions
)
# from edu_meet_bot.debug.utils import log_json_data


logger = logging.getLogger(__name__)

router = Router(name="edu_meet_bot/registration")


@router.message(F.text == "Записаться на занятие")
async def receive_registration_request(message: Message) -> None:
    await message.answer(
        'Цена на занятие 2500р./ 1 час\n'
        'Выберите удобный вам день и время занятия.\n'
        'После предоплаты 50% заказ будет подтвержден.',
        reply_markup=select_date(
            user_id=message.from_user.id, user_name=message.from_user.username
        )
    )


# routes.py
@router.callback_query(F.data.startswith('select_date|'))
@handle_exceptions
async def on_select_date_click(callback: CallbackQuery) -> None:
    logging.info(f'callback.data: {callback.data}')
    today = datetime.now().date()
    month_later = today + timedelta(weeks=4)

    async with async_session() as db_session:
        # Получаем доступные слоты
        slots = await get_available_slots(db_session, today, month_later)
    logging.info(f'slots: {slots}')

    if not slots:
        await handle_no_slots(callback.message, "месяц")
        return

    # Группируем слоты по неделям
    weeks = group_slots_by_time_period(slots, period='week')

    # Создаем клавиатуру для выбора недели
    keyboard = create_period_selection_keyboard(
        weeks,
        label_func=lambda week_start: f"{week_start.strftime('%d.%m.%Y')} - "
                                      f"{(week_start + timedelta(days=6)).strftime('%d.%m.%Y')}",
        callback_prefix="select_week"
    )

    # Отправляем сообщение с выбором недели
    await callback.message.edit_text(
        "Выберите неделю для записи:",
        reply_markup=keyboard
    )
    logging.info("Сообщение с выбором недели отправлено.")


@router.callback_query(F.data.startswith('select_week|'))
@handle_exceptions
async def on_select_week_click(callback: CallbackQuery) -> None:
    logging.info(f'callback.data: {callback.data}')
    _, week_start_str = callback.data.split('|')
    week_start = datetime.fromisoformat(week_start_str).date()
    week_end = week_start + timedelta(days=6)

    async with async_session() as db_session:
        # Получаем слоты в пределах выбранной недели
        slots = await get_available_slots(db_session, week_start, week_end)
    logging.info(f'Слоты для недели {week_start} - {week_end}: {slots}')

    if not slots:
        await handle_no_slots(callback.message, f"неделю с {week_start.strftime('%d.%m.%Y')} по {week_end.strftime('%d.%m.%Y')}")
        return

    # Группируем слоты по дням
    days = group_slots_by_time_period(slots, period='day')

    # Создаем клавиатуру для выбора дня
    keyboard = create_period_selection_keyboard(
        days,
        label_func=lambda day: day.strftime('%A, %d.%m.%Y'),
        callback_prefix="select_day"
    )

    # Отправляем сообщение с выбором дня
    await callback.message.edit_text(
        f"Выберите день недели с {week_start.strftime('%d.%m.%Y')} по {week_end.strftime('%d.%m.%Y')}:",
        reply_markup=keyboard
    )
    logging.info("Сообщение с выбором дня отправлено.")



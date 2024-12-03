from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.registration.views import select_date
from datetime import datetime, timedelta
from edu_meet_bot.db import async_session
import logging
import traceback
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period,
    create_week_selection_keyboard, handle_no_slots,
    handle_exceptions, create_time_selection_keyboard,
    create_day_selection_keyboard
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


@router.callback_query(F.data.startswith('select_date|'))
@handle_exceptions
async def on_select_date_click(callback: CallbackQuery) -> None:
    today = datetime.now().date()
    logging.info(f"Сегодняшняя дата ++++++++++++++++++= : {today}")
    async with async_session() as db_session:
        # Получаем доступные слоты
        slots = await get_available_slots(db_session, today)

    if not slots:
        await handle_no_slots(callback.message, "месяц")
        return

    logging.info(f"Слоты после выборки +++++++++++++++ : {[slot.date for slot in slots]}")

    # Группируем слоты по неделям
    weeks = group_slots_by_time_period(slots, period='week', today=today)


    # Создаем клавиатуру для выбора недели
    keyboard = create_week_selection_keyboard(
        weeks,
        label_func=lambda start, end: f"{start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}",

        callback_prefix="select_week"
    )

    # Отправляем сообщение с выбором недели
    await callback.message.edit_text(
        "Выберите неделю для записи:",
        reply_markup=keyboard
    )



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
    logging.info(f'Слоты для недели {week_start} - {week_end}: \n{slots}\n')

    if not slots:
        await handle_no_slots(callback.message, f"неделю с {week_start.strftime('%d.%m.%Y')} по {week_end.strftime('%d.%m.%Y')}")
        return

    # Группируем слоты по дням
    days = group_slots_by_time_period(slots, period='day')

    # Создаем клавиатуру для выбора дня
    keyboard = create_day_selection_keyboard(
        period=days,
        label_func=lambda day: day.strftime('%A, %d.%m.%Y'),
        callback_prefix="select_day"
    )

    # Отправляем сообщение с выбором дня
    await callback.message.edit_text(
        f"Выберите день недели с {week_start.strftime('%d.%m.%Y')} по {week_end.strftime('%d.%m.%Y')}:",
        reply_markup=keyboard
    )
    logging.info("Сообщение с выбором дня отправлено.")


@router.callback_query(F.data.startswith('select_day|'))
async def on_select_day_click(callback: CallbackQuery) -> None:
    logging.info(f'callback ++++++++++++++++ : {callback}')
    try:
        # Извлекаем дату дня из callback_data
        _, day_str = callback.data.split('|')
        selected_day = datetime.fromisoformat(day_str).date()

        async with async_session() as db_session:
            # Получаем доступные слоты для выбранного дня
            slots = await get_available_slots(db_session, selected_day, selected_day)
        logging.info(f'Слоты для дня {selected_day}: {slots}')

        # Проверяем, есть ли доступные слоты
        if not slots:
            return await handle_no_slots(callback.message, period_desc="день")

        # Создаем клавиатуру для выбора времени
        keyboard = create_time_selection_keyboard(
            slots,
            label_func=lambda slot: f"{slot.time_start.strftime('%H:%M')} - {slot.time_end.strftime('%H:%M')}",
            callback_prefix="select_time"
        )

        # Отправляем сообщение с выбором времени
        await callback.message.edit_text(
            f"Выберите время на {selected_day.strftime('%A, %d.%m.%Y')}:",
            reply_markup=keyboard
        )
        logging.info("Сообщение с выбором времени отправлено.")

    except Exception as e:
        logging.error(f"Ошибка при обработке дня: {e}")
        logging.error(traceback.format_exc())
        await callback.message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )

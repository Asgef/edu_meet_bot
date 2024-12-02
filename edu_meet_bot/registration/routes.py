from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.support.fsm import StepsQuestionMessage, StepsAnswerMessage
from aiogram.fsm.context import FSMContext
from edu_meet_bot import settings
from edu_meet_bot.support.utils import escape_markdown
from edu_meet_bot.registration.views import select_date
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from sqlalchemy import select
from edu_meet_bot.session.models import Slot
from edu_meet_bot.db import async_session
from edu_meet_bot.session.enum_fields import SlotStatus
import logging
import traceback
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_weeks, create_week_selection_keyboard
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
async def on_select_date_click(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'callback.data: {callback.data}')
    today = datetime.now().date()
    month_later = today + timedelta(weeks=4)

    try:
        async with async_session() as db_session:
            # Получаем доступные слоты
            slots = await get_available_slots(db_session, today, month_later)
        logging.info(f'slots: {slots}')

        if not slots:
            await callback.message.answer(
                "На ближайший месяц нет доступных недель для записи."
            )
            return

        # Группируем слоты по неделям
        weeks = group_slots_by_weeks(slots)

        # Создаем клавиатуру для выбора недели
        keyboard = create_week_selection_keyboard(weeks)

        # Отправляем сообщение с выбором недели
        await callback.message.answer(
            "Выберите неделю для записи:",
            reply_markup=keyboard
        )
        logging.info("Сообщение с выбором недели отправлено.")

    except Exception as e:
        logging.error(f"Ошибка при обработке слотов: {e}")
        logging.error(traceback.format_exc())
        await callback.message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )


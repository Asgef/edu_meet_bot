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
    user_id = callback.from_user.id

    today = datetime.now().date()
    month_later = today + timedelta(weeks=4)

    try:
        async with async_session() as db_session:
            conditions = [
                Slot.date >= today,
                Slot.date <= month_later,
                Slot.status == SlotStatus.AVAILABLE.value
            ]

            for condition in conditions:
                logging.info(f'Condition: {condition}')

            query = select(Slot).where(*conditions)
            logging.info(f'Executing query: {query}')
            result = await db_session.execute(query)
            slots = result.scalars().all()
        logging.info(f'slots: {slots}')
        if not slots:
            await callback.message.answer(
                "На ближайший месяц нет доступных недель для записи."
            )
            return

        # Шаг 3: Группируем слоты по неделям
        weeks = {}
        for slot in slots:
            week_start = slot.date.date() - timedelta(days=slot.date.weekday())
            weeks.setdefault(week_start, []).append(slot)

        # Шаг 4: Создаем кнопки для выбора недели
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])  # Создаем объект с пустым списком кнопок
        for week_start in sorted(weeks.keys()):
            week_label = f"{week_start.strftime('%d.%m.%Y')} - {(week_start + timedelta(days=6)).strftime('%d.%m.%Y')}"
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=week_label,
                    callback_data=f"select_week|{week_start.isoformat()}"
                )
            ])

        # Шаг 5: Отправляем сообщение пользователю
        try:
            logging.info("Отправляем сообщение с выбором недели...")
            await callback.message.answer(
                "Выберите неделю для записи:",
                reply_markup=keyboard
            )
            logging.info("Сообщение с выбором недели отправлено.")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
            logging.error(traceback.format_exc())
            await callback.message.answer(
                "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logging.error(f"Ошибка при обработке слотов: {e}")
        logging.error(traceback.format_exc())
        await callback.message.answer(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )
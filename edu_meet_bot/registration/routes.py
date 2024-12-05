from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.registration.views import select_date
from datetime import datetime
from edu_meet_bot.db import async_session
import logging
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period, handle_no_slots,
    handle_exceptions, get_academic_subjects, get_usr_id, get_daily_slots
)
from edu_meet_bot.registration.views import (
    select_week, select_slot, select_day, register_button,
    register_button_academic_subject
)
from aiogram.fsm.context import FSMContext

from edu_meet_bot.session.enum_fields import OrderStatus, SlotStatus
from edu_meet_bot.settings import TUTOR_TG_ID
from edu_meet_bot.session.models import Order, Slot
from aiogram.filters.state import StateFilter


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
    today = datetime.now().date()  # Текущая дата
    now_time = datetime.now().time()  # Текущее время
    logging.info(f'Сегодня >>>>>>>>>>>>>: {today}, Текущее время: {now_time}')

    async with async_session() as db_session:
        # Получаем доступные слоты
        slots = await get_available_slots(
            db_session, start_date=today, current_time=now_time
        )

    if not slots:
        await handle_no_slots(callback.message, "месяц")
        return

    logging.info(f'Слоты >>>>>>>>>>>>>>>>>: {slots}')

    # Группируем слоты по неделям
    weeks = group_slots_by_time_period(slots, period='week', today=today)

    # Создаем клавиатуру для выбора недели
    keyboard = select_week(
        weeks,
        label_func=lambda start, end:
        f"{start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}",
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
    _, week_start_str, week_end_str = callback.data.split('|')
    week_start = datetime.fromisoformat(week_start_str).date()
    week_end = datetime.fromisoformat(week_end_str).date()

    async with async_session() as db_session:
        # Получаем слоты в пределах выбранной недели
        slots = await get_available_slots(db_session, week_start, week_end)

    logging.info(f'Недельные слоты >>>>>>>>>>>>>>>>>: {slots}')

    if not slots:
        await handle_no_slots(
            callback.message,
            f"неделю с {week_start.strftime('%d.%m.%Y')} по "
            f"{week_end.strftime('%d.%m.%Y')}"
        )
        return

    # Группируем слоты по дням
    days = group_slots_by_time_period(slots, period='day')

    # Создаем клавиатуру для выбора дня
    keyboard = select_day(
        period=days,
        label_func=lambda day: day.strftime('%A, %d.%m.%Y'),
        callback_prefix="select_day"
    )

    # Отправляем сообщение с выбором дня
    await callback.message.edit_text(
        f"Выберите день недели с {week_start.strftime('%d.%m.%Y')} по "
        f"{week_end.strftime('%d.%m.%Y')}:",
        reply_markup=keyboard
    )
    logging.info("Сообщение с выбором дня отправлено.")


@router.callback_query(F.data.startswith('select_day|'))
@handle_exceptions
async def on_select_day_click(callback: CallbackQuery) -> None:
    # Извлекаем дату дня из callback_data
    _, day_str = callback.data.split('|')
    selected_day = datetime.fromisoformat(day_str).date()

    async with async_session() as db_session:
        # Получаем доступные слоты для выбранного дня
        slots = await get_daily_slots(
            db_session, selected_day, datetime.now().time()
        )
    slots.sort(key=lambda slot: slot.time_start)
    logging.info(f'Слоты для дня >>>>>>>>>>>>>> {selected_day}: {slots}')

    # Проверяем, есть ли доступные слоты
    if not slots:
        return await handle_no_slots(callback.message, period_desc="день")

    # Создаем клавиатуру для выбора времени
    keyboard = select_slot(
        slots,
        label_func=lambda slot: f"{slot.time_start.strftime('%H:%M')} - "
                                f"{slot.time_end.strftime('%H:%M')}",
        callback_prefix="select_slot"
    )

    # Отправляем сообщение с выбором времени
    await callback.message.edit_text(
        f"Выбери время на {selected_day.strftime('%A, %d.%m.%Y')}:",
        reply_markup=keyboard
    )
    logging.info("Сообщение с выбором времени отправлено.")


@router.callback_query(F.data.startswith('select_slot|'))
@handle_exceptions
async def on_select_slot_click(callback: CallbackQuery) -> None:
    # Извлекаем данные из callback_data
    _, slot_id, slot_time = callback.data.split('|')
    slot_id = int(slot_id)

    # Отправляем сообщение с информацией о выбранном слоте
    await callback.message.edit_text(
        f'Регистрация на занятие в {slot_time}.\n',
        reply_markup=register_button(slot_id)
    )


@router.callback_query(F.data.startswith('register_academic_subject|'))
@handle_exceptions
async def on_register_subject_click(
        callback: CallbackQuery, state: FSMContext
) -> None:
    # Извлекаем slot_id из callback_data
    _, slot_id = callback.data.split('|')
    slot_id = int(slot_id)

    # Сохраняем slot_id в FSM
    await state.update_data(slot_id=slot_id)

    # Получаем список предметов
    async with async_session() as db_session:
        subjects = await get_academic_subjects(db_session)

    # Создаем клавиатуру для выбора предмета
    keyboard = register_button_academic_subject(subjects)

    # Отправляем сообщение пользователю
    await callback.message.edit_text(
        "Выберите учебный предмет:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith('select_subject|'))
@handle_exceptions
async def on_subject_selected(
        callback: CallbackQuery, state: FSMContext
) -> None:
    # Извлекаем subject_id из callback_data
    _, subject_id = callback.data.split('|')
    subject_id = int(subject_id)

    # Сохраняем subject_id в FSM
    await state.update_data(subject_id=subject_id)

    # Сообщение пользователю о вводе комментария
    await callback.message.edit_text(
        "Введите комментарий.\n\n"
        "Представься, задай вопрос или просто кажи 'Привет' "
    )

    # Устанавливаем состояние ожидания комментария
    await state.set_state("waiting_for_comment")


@router.message(StateFilter("waiting_for_comment"))
@handle_exceptions
async def on_comment_entered(message: Message, state: FSMContext) -> None:
    # Получаем введённый комментарий
    comment = message.text

    # Извлекаем данные из FSM
    data = await state.get_data()
    slot_id = data["slot_id"]
    subject_id = data["subject_id"]

    # Получаем id студента и репетитора
    async with async_session() as db_session:
        student_id = await get_usr_id(db_session, message.from_user.id)
        tutor_id = await get_usr_id(db_session, TUTOR_TG_ID)
        slot = await db_session.get(Slot, slot_id)

        # Проверяем статус слота, слот может уже быть занят
        if slot.status != SlotStatus.AVAILABLE:
            await message.answer(
                "Слот уже занят. Пожалуйста, выберите другой."
            )
            await state.clear()
            return

        # Обновляем статус слота
        slot.status = SlotStatus.PENDING
        slot.student_id = student_id

        # Создаем экземпляр Order
        order = Order(
            student_id=student_id,
            tutor_id=tutor_id,
            slot_id=slot_id,
            subject_id=subject_id,
            status=OrderStatus.PENDING,
            comment=comment,
            date=slot.date,
        )
        db_session.add(order)

        # Сохраняем изменения
        await db_session.commit()

    # Отправляем сообщение пользователю
    formatted_date = slot.date.strftime("%d.%m.%Y")

    await message.answer(
        f"Вы успешно зарегистрировались на занятие!\n"
        f"Дата: {formatted_date} {slot.time_start}-{slot.time_end}, "
        f"Предмет: {subject_id}, Комментарий: {comment}"
    )

    # Очистка состояния
    await state.clear()

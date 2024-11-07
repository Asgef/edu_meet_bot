from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from edu_meet_bot.support.fsm import StepsQuestionMessage
from aiogram.fsm.context import FSMContext
from edu_meet_bot import settings
# from edu_meet_bot.debug.utils import log_json_data

router = Router(name="edu_meet_bot/support")


@router.message(Command("getchatid"))
# @log_json_data
async def get_chat_id(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.answer(
        f"Chat id is: *{chat_id}*\n"
        f"Your id is: *{user_id}*", parse_mode='Markdown'
    )


@router.message(F.text == "Связаться с репетитором")
async def get_question_message(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Задайте ваш вопрос репетитору, он ответит как только освободится:'
    )
    await state.set_state(StepsQuestionMessage.GET_MASSAGE)


@router.message(StepsQuestionMessage.GET_MASSAGE)
async def send_question_massage(
        message: Message, state: FSMContext, bot: Bot
) -> None:
    user = message.from_user.username or message.from_user.first_name
    question_text = message.caption\
        if message.content_type == 'photo' else message.text

    if message.content_type == 'photo' and message.photo:
        photo_id = message.photo[-1].file_id
        await bot.send_photo(
            settings.SUPPORT_CHAT_ID,
            photo=photo_id,
            caption=(
                f"✉ | Новый вопрос\nОт: {user}\nВопрос: `{question_text}`\n\n"
                f"📝 Чтобы ответить на вопрос введите `/ответ {message.chat.id} Ваш ответ`"  # noqa E501
            ),
            parse_mode='Markdown'
        )
    else:
        await bot.send_message(
            settings.SUPPORT_CHAT_ID,
            text=(
                f"✉ | Новый вопрос\nОт: {user}\nВопрос: `{question_text}`\n\n"
                f"📝 Чтобы ответить на вопрос введите `/ответ {message.chat.id} Ваш ответ`"  # noqa E501
            ),
            parse_mode='Markdown'
        )

    await message.reply(
        'Ваш вопрос был отослан! Ожидайте ответа.',
        parse_mode='Markdown'
    )
    await state.clear()

from edu_meet_bot.support.errors import InvalidUserIdError
import logging


def extract_arg(text_message: str) -> tuple:
    data = text_message.split()

    if len(data) <= 2 or not data[1].isdigit():
        raise InvalidUserIdError

    chat_id = data[1]
    answer = ' '.join(data[2:])
    return chat_id, answer

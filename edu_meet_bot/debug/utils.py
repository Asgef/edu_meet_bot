import json
import logging
from functools import wraps


logger = logging.getLogger(__name__)


def log_json_data(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Ищем параметр `message`, если он передан
        message = kwargs.get('message') or (args[0] if args else None)

        # Если message — объект с методом dict, преобразуем его в JSON
        if message and hasattr(message, "dict"):
            json_str = json.dumps(message.dict(), default=str, indent=4)
            logger.info(f"Message JSON:\n{json_str}")

        # Выполняем основную функцию
        return await func(*args, **kwargs)

    return wrapper

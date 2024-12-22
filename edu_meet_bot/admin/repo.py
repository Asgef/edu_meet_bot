from sqlalchemy import exists, select, update, Update, Select
from edu_meet_bot.general_menu.models import User


def is_user_admin_by_tg_id(tg_id: int) -> Select:
    return exists(User.id).where(
        User.tg_id == tg_id, User.is_admin
    ).select()


def get_user_by_tg_id(tg_id: int) -> Select:
    return select(User).where(User.tg_id == tg_id)


def change_user_admin_status_by_id(tg_id: int, is_admin: bool) -> Update:
    # Подготавливаем запрос на обновление
    return (
        update(User)
        .where(User.tg_id == tg_id)
        .values(is_admin=is_admin)
    )

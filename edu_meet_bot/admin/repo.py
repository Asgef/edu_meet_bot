# from sqlalchemy import exists, select, update
#
# from edu_meet_bot.admin.models import AdminUser
#
#
# def is_user_admin_by_tg_id(id: int):
#     return exists(AdminUser.id).where(AdminUser.user_id == id,
#                                       AdminUser.is_admin).select()
#
#
# def get_user_by_tg_id(id: int):
#     return select(AdminUser).where(AdminUser.user_id == id)
#
#
# def change_user_admin_status_by_id(id: int, is_admin: bool):
#     return update(AdminUser).where(AdminUser.id == id).values(
#         is_admin=is_admin)

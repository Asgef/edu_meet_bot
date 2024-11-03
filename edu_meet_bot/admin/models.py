from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from edu_meet_bot.base_model import BaseModel


# class AdminUser(BaseModel):
#     __tablename__ = "admin_users"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int]
#
#     is_admin: Mapped[bool] = mapped_column(default=True)
#
#     created_at: Mapped[datetime] = mapped_column(default=func.now())
#     updated_at: Mapped[datetime] = mapped_column(default=func.now(),
#                                                  onupdate=func.now())

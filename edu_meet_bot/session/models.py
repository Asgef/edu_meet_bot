# from datetime import datetime
# from decimal import Decimal
# from typing import List
#
# from sqlalchemy import Column, ForeignKey, Numeric, Table
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy.sql import func
#
# from edu_meet_bot.base_model import BaseModel
#
#
# class Order(BaseModel):
#     __tablename__ = "order"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     student_name: Mapped[str] = mapped_column(nullable=True)
#     student_contact: Mapped[str] = mapped_column(nullable=True)
#     order_date: Mapped[datetime] = mapped_column(default=func.now())
#
#
#
#     price: Mapped[Decimal] = mapped_column(Numeric(10, 4))
#     photo: Mapped[str] = mapped_column(nullable=True)
#
#     added_by_user: Mapped[int]
#
#     archived: Mapped[bool] = mapped_column(default=False)
#
#     created_at: Mapped[datetime] = mapped_column(default=func.now())
#     updated_at: Mapped[datetime] = mapped_column(default=func.now(),
#                                                  onupdate=func.now())

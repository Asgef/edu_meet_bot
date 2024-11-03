from datetime import datetime
from decimal import Decimal
from secrets import choice
from typing import List
from sqlalchemy import Enum, Time, ForeignKey, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from edu_meet_bot.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    timezone: Mapped[Decimal] = mapped_column(default=Decimal(0))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Slot(BaseModel):
    __tablename__ = "slot"

    CHOOSES = (
        'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday'
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slot_time: Mapped[str] = mapped_column(nullable=False)
    day_of_week: Mapped[str] = mapped_column(
        Enum(*CHOOSES, name='day_of_week_enum'), nullable=False)
    hour: Mapped[Time] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True)
    is_recurring: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (
            f"<Slot(id={self.id}, day_of_week={self.day_of_week}, "
            f"hour={self.hour})>"
        )


class AcademicSubject(BaseModel):
    __tablename__ = "academic_subject"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<AcademicSubject(id={self.id}, name={self.name})>"


class Order(BaseModel):
    __tablename__ = 'orders'

    CHOICES = ('pending', 'accepted', 'declined', 'canceled')

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    tutor_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    slot_id: Mapped[int] = mapped_column(ForeignKey('slot.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('academic_subject.id'))
    status: Mapped[str] = mapped_column(
        Enum(*CHOICES, name='status_enum'), nullable=False
    )
    comment: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[Date] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(onupdate=func.now())

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    tutor = relationship("User", foreign_keys=[tutor_id])
    slot = relationship("Slot")

    def __repr__(self):
        return (
            f"<Order(id={self.id}, student_id={self.student_id}, "
            f"slot_id={self.slot_id})>"
        )


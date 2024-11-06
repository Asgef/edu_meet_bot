from datetime import datetime, time
from sqlalchemy import Enum, ForeignKey, BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from edu_meet_bot.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(unique=True, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    timezone: Mapped[str] = mapped_column(String, default="Europe/Moscow")
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Slot(BaseModel):
    __tablename__ = "slot"

    CHOOSES = (
        'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday'
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day_of_week: Mapped[str] = mapped_column(
        Enum(*CHOOSES, name='day_of_week_enum'), nullable=False)
    hour: Mapped[time] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(default=60)
    is_available: Mapped[bool] = mapped_column(default=True)
    is_recurring: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (
            f"<Slot(id={self.id}, day_of_week={self.day_of_week}, "
            f"hour={self.hour})>"
        )


class AcademicSubject(BaseModel):
    __tablename__ = "academic_subject"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<AcademicSubject(id={self.id}, name={self.name})>"


class Order(BaseModel):
    __tablename__ = 'order'

    CHOICES = ('pending', 'accepted', 'declined', 'canceled')

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    tutor_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    slot_id: Mapped[int] = mapped_column(ForeignKey('slot.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('academic_subject.id'))
    status: Mapped[str] = mapped_column(
        Enum(*CHOICES, name='status_enum'), nullable=False
    )
    comment: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    tutor = relationship("User", foreign_keys=[tutor_id])
    slot = relationship("Slot")

    def __repr__(self):
        return (
            f"<Order(id={self.id}, student_id={self.student_id}, "
            f"slot_id={self.slot_id})>"
        )

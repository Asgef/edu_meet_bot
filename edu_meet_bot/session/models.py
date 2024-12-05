from datetime import datetime, time, date
from sqlalchemy import ForeignKey, BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Date, Time
from edu_meet_bot.base_model import BaseModel
from edu_meet_bot.session.enum_fields import SlotStatus, OrderStatus
from sqlalchemy import Enum as SQLAlchemyEnum


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    username: Mapped[str] = mapped_column(
        String(150), nullable=True
    )
    first_name: Mapped[str] = mapped_column(
        String(150), nullable=True
    )
    last_name: Mapped[str] = mapped_column(
        String(150), nullable=True
    )

    is_admin: Mapped[bool] = mapped_column(default=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    tutor_slots = relationship(
        "Slot", foreign_keys="Slot.tutor_id", back_populates="tutor"
    )
    student_slots = relationship(
        "Slot", foreign_keys="Slot.student_id", back_populates="student"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Slot(BaseModel):
    __tablename__ = "slot"

    SLOT_CHOICES = ('available', 'pending', 'accepted',)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time_start: Mapped[time] = mapped_column(Time, nullable=False)
    time_end: Mapped[time] = mapped_column(Time, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=True
    )
    status: Mapped[SlotStatus] = mapped_column(
        SQLAlchemyEnum(
            SlotStatus,
            name='slot_status_enum',
            values_callable=lambda x: [e.value for e in x],
            native_enum=False
        ),
        nullable=False,
        default=SlotStatus.AVAILABLE.value
    )

    comment: Mapped[str] = mapped_column(String(255), nullable=True)

    tutor = relationship(
        "User", foreign_keys=[tutor_id], back_populates="tutor_slots"
    )
    student = relationship(
        "User", foreign_keys=[student_id], back_populates="student_slots"
    )

    def __repr__(self):
        return (
            f"<Slot(id={self.id}, date={self.date}, "
            f"time_start={self.time_start}, status={self.status})>"
        )


class AcademicSubject(BaseModel):
    __tablename__ = "academic_subject"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(1000), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<AcademicSubject(id={self.id}, name={self.name})>"


class Order(BaseModel):
    __tablename__ = 'order'

    ORDER_CHOICES = ('pending', 'accepted', 'declined', 'canceled')

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    tutor_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    slot_id: Mapped[int] = mapped_column(ForeignKey('slot.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('academic_subject.id'))
    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(
            OrderStatus,
            name='order_status_enum',
            values_callable=lambda x: [e.value for e in x],
            native_enum=False
        ),
        nullable=False,
        default=OrderStatus.PENDING.value
    )
    comment: Mapped[str] = mapped_column(String(255), nullable=True)
    date: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    tutor = relationship("User", foreign_keys=[tutor_id])
    slot = relationship("Slot")

    def __repr__(self):
        return (
            f"<Order(id={self.id}, student_id={self.student_id}, "
            f"slot_id={self.slot_id}, status={self.status})>"
        )

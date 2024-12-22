import enum


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"
    PENDING = "pending"
    ACCEPTED = "accepted"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELED = "canceled"

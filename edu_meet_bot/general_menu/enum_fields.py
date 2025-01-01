import enum


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"
    PENDING = "pending"
    ACCEPTED = "accepted"
    UNAVAILABLE = "unavailable"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELED = "canceled"

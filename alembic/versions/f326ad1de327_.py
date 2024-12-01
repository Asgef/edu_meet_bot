"""empty message

Revision ID: f326ad1de327
Revises: b66910d86c4b
Create Date: 2024-12-01 13:26:25.671989+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = 'f326ad1de327'
down_revision: Union[str, None] = 'b66910d86c4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Определяем новый тип ENUM для order
order_status_enum = ENUM('pending', 'accepted', 'declined', 'canceled', name='order_status_enum', create_type=False)

# Определяем новый тип ENUM для slot
slot_status_enum = ENUM('available', 'pending', 'accepted', name='slot_status_enum', create_type=False)


def upgrade() -> None:
    # Создаем новый тип ENUM для order
    order_status_enum.create(op.get_bind())
    # Создаем новый тип ENUM для slot
    slot_status_enum.create(op.get_bind())

    # Изменяем колонку status в таблице order
    op.execute(
        """
        ALTER TABLE "order"
        ALTER COLUMN status TYPE order_status_enum
        USING status::text::order_status_enum
        """
    )

    # Изменяем колонку status в таблице slot
    op.execute(
        """
        ALTER TABLE "slot"
        ALTER COLUMN status TYPE slot_status_enum
        USING status::text::slot_status_enum
        """
    )


def downgrade() -> None:
    # Возвращаем колонку status в таблице order к старому типу ENUM
    op.execute(
        """
        ALTER TABLE "order"
        ALTER COLUMN status TYPE VARCHAR
        USING status::text
        """
    )

    # Возвращаем колонку status в таблице slot к старому типу ENUM
    op.execute(
        """
        ALTER TABLE "slot"
        ALTER COLUMN status TYPE VARCHAR
        USING status::text
        """
    )

    # Удаляем новый тип ENUM для order
    order_status_enum.drop(op.get_bind())

    # Удаляем новый тип ENUM для slot
    slot_status_enum.drop(op.get_bind())

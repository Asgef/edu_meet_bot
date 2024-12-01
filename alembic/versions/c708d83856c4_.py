"""empty message

Revision ID: c708d83856c4
Revises: dea0023a4444
Create Date: 2024-12-01 11:01:36.516496+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c708d83856c4'
down_revision: Union[str, None] = 'dea0023a4444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('slot', sa.Column('status', sa.Enum('available', 'pending', 'accepted', name='status_enum'), nullable=False))
    op.drop_column('slot', 'is_available')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('slot', sa.Column('is_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('slot', 'status')
    # ### end Alembic commands ###
"""created_at and updated_at fields in task model

Revision ID: bb8fdb1bb2a8
Revises: e3a46aff14a3
Create Date: 2025-04-03 13:56:49.411163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb8fdb1bb2a8'
down_revision: Union[str, None] = 'e3a46aff14a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
    op.add_column('tasks', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'updated_at')
    op.drop_column('tasks', 'created_at')
    # ### end Alembic commands ###

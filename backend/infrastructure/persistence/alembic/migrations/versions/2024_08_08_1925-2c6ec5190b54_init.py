"""init

Revision ID: 2c6ec5190b54
Revises: 
Create Date: 2024-08-08 19:25:40.535246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c6ec5190b54'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('full_name', sa.String(length=128), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('phone_number', sa.String(length=12), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Дата обновления записи'),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Дата создания записи'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###

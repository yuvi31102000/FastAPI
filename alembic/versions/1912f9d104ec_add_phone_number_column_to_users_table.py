"""add phone number column to users table

Revision ID: 1912f9d104ec
Revises: 678aafe29f76
Create Date: 2025-08-15 21:29:29.913653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1912f9d104ec'
down_revision: Union[str, Sequence[str], None] = '678aafe29f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=False))


def downgrade() -> None:
    """Downgrade schema.""" 
    op.drop_column('users', 'phone_number')

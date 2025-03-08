"""Added urls table

Revision ID: 9d46ee2b448f
Revises: 
Create Date: 2025-03-08 17:57:50.816374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d46ee2b448f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass
    op.create_table(
        'URLs',
        sa.Column('short_url', sa.String, primary_key=True),
        sa.Column('long_url', sa.String),
        sa.Column('expiry', sa.Integer)
        )



def downgrade() -> None:
    """Downgrade schema."""
    pass
    op.drop_table('URLs')

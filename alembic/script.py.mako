"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}
    op.create_table(
        'URLS',
        sa.Column('short_url', sa.String, primary_key=True),
        sa.Column('long_url', sa.String),
        sa.Column('expiry', sa.Integer)
        )



def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
    op.drop_table('URLS')

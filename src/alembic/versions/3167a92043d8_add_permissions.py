"""add permissions

Revision ID: 3167a92043d8
Revises: 35f283379183
Create Date: 2025-07-05 09:20:39.167805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3167a92043d8'
down_revision: Union[str, None] = '35f283379183'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    from sqlalchemy.sql import table, column
    from sqlalchemy import String
    from sqlalchemy.dialects import postgresql

    permissions_table = table(
        'permissions',
        column('permission', String),
    )

    op.execute("""
        INSERT INTO permissions (permission) VALUES
        ('owner'::permission),
        ('invite_members'::permission),
        ('kick_members'::permission),
        ('promote_members'::permission),
        ('wars'::permission);
    """)

def downgrade():
    op.execute("DELETE FROM permissions")
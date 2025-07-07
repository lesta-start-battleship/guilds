"""merge roles_promotes and war_id migrations

Revision ID: 5e28a9b50d59
Revises: dc0888ba7f00, c27884beb6d4
Create Date: 2025-07-07 20:11:58.053484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e28a9b50d59'
down_revision: Union[str, None] = ('dc0888ba7f00', 'c27884beb6d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

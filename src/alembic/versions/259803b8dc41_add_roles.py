"""add roles

Revision ID: 259803b8dc41
Revises: 3167a92043d8
Create Date: 2025-07-05 09:28:18.592859

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '259803b8dc41'
down_revision: Union[str, None] = '3167a92043d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO roles (title) VALUES ('owner'), ('cabin_boy'), ('officer');")

    op.execute("""
        INSERT INTO role_permission (role_id, permission_id)
        SELECT r.id, p.id FROM roles r, permissions p WHERE r.title = 'owner';
        """)
    
    op.execute("""    
        INSERT INTO role_permission (role_id, permission_id)
        SELECT r.id, p.id FROM roles r, permissions p
        WHERE r.title = 'officer' AND p.permission IN ('invite_members', 'kick_members', 'promote_members')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM role_permission")
    op.execute("DELETE FROM roles")
    
    

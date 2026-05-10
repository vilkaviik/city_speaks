"""is_active at trend

Revision ID: 2da5f7e522f2
Revises: 4f3011710093
Create Date: 2026-05-06 15:10:29.131778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2da5f7e522f2'
down_revision: Union[str, Sequence[str], None] = '4f3011710093'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""add centroid to trends

Revision ID: c699720f0cb0
Revises: 8035c2ddb111
Create Date: 2026-04-14 15:44:01.179444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c699720f0cb0'
down_revision: Union[str, Sequence[str], None] = '8035c2ddb111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

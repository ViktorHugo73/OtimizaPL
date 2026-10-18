"""Persist inputs and named results for reproducible resource analysis."""
from alembic import op
import sqlalchemy as sa

revision = 'e71c9a04b632'
down_revision = '13a8bb78d1db'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('executions', sa.Column('analysis_snapshot', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('executions', 'analysis_snapshot')

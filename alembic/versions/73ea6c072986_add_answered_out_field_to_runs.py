"""add answered out field to runs

Revision ID: 73ea6c072986
Revises: 43018c296295
Create Date: 2017-02-23 14:54:25.228041

"""

# revision identifiers, used by Alembic.
revision = '73ea6c072986'
down_revision = '43018c296295'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis_run', sa.Column('answeredout_at', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analysis_run', 'answeredout_at')
    ### end Alembic commands ###
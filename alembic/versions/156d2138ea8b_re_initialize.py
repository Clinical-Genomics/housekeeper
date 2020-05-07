"""re-initialize

Revision ID: 156d2138ea8b
Revises: 
Create Date: 2017-01-23 08:04:16.177540

"""

# revision identifiers, used by Alembic.
revision = "156d2138ea8b"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column("sample", sa.Column("priority", sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sample", "priority")
    ### end Alembic commands ###

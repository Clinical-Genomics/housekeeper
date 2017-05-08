"""add comment field to case

Revision ID: cd9166dd20cf
Revises: ac9547bfbf42
Create Date: 2017-05-08 09:49:49.663953

"""

# revision identifiers, used by Alembic.
revision = 'cd9166dd20cf'
down_revision = 'ac9547bfbf42'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('case', sa.Column('comment', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('case', 'comment')
    ### end Alembic commands ###

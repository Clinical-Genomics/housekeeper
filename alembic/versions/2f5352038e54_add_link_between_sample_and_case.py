"""add link between sample and case

Revision ID: 2f5352038e54
Revises: 156d2138ea8b
Create Date: 2017-02-07 11:06:17.737229

"""

# revision identifiers, used by Alembic.
revision = '2f5352038e54'
down_revision = '156d2138ea8b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sample', sa.Column('case_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'sample', 'case', ['case_id'], ['id'])
    op.drop_column('sample', 'customer')
    op.drop_column('sample', 'family_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sample', sa.Column('family_id', mysql.VARCHAR(length=128), nullable=False))
    op.add_column('sample', sa.Column('customer', mysql.VARCHAR(length=32), nullable=False))
    op.drop_constraint(None, 'sample', type_='foreignkey')
    op.drop_column('sample', 'case_id')
    ### end Alembic commands ###
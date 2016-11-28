"""add user management

Revision ID: ab7dc4d7408a
Revises: e5d3b6f4e074
Create Date: 2016-11-09 15:01:12.829653

"""

# revision identifiers, used by Alembic.
revision = 'ab7dc4d7408a'
down_revision = 'e5d3b6f4e074'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('google_id', sa.String(length=128), nullable=True),
        sa.Column('email', sa.String(length=128), nullable=True),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('avatar', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )
    op.create_table('flask_dance_oauth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('token', sqlalchemy_utils.types.json.JSONType(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], [u'user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('flask_dance_oauth')
    op.drop_table('user')
    ### end Alembic commands ###
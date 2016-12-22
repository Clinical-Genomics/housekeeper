"""add extra data table to replace JSON field for run

Revision ID: 1b0a755720b2
Revises: ab7dc4d7408a
Create Date: 2016-12-15 15:00:33.905770

"""

# revision identifiers, used by Alembic.
revision = '1b0a755720b2'
down_revision = 'ab7dc4d7408a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('extra_run_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.Column('coverage_date', sa.DateTime(), nullable=True),
    sa.Column('frequency_date', sa.DateTime(), nullable=True),
    sa.Column('genotype_date', sa.DateTime(), nullable=True),
    sa.Column('visualizer_date', sa.DateTime(), nullable=True),
    sa.Column('rawdata_date', sa.DateTime(), nullable=True),
    sa.Column('qc_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['run_id'], ['analysis_run.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('run_id')
    )
    op.drop_table('flask_dance_oauth')
    op.drop_column('analysis_run', 'added_dates')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis_run', sa.Column('added_dates', mysql.TEXT(), nullable=True))
    op.create_table('flask_dance_oauth',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('provider', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('token', mysql.TEXT(), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'flask_dance_oauth_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'latin1',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('extra_run_data')
    ### end Alembic commands ###
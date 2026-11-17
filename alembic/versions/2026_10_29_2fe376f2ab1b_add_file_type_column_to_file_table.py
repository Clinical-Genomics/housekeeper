"""Add file type column to File table

Revision ID: 2fe376f2ab1b
Revises: f1669dd42064
Create Date: 2026-10-29 14:43:57.871836

"""

# revision identifiers, used by Alembic.
revision = "2fe376f2ab1b"
down_revision = "f1669dd42064"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        table_name="file",
        column=sa.Column(
            name="file_type", nullable=True, type_=sa.String(128), default=None, index=True
        ),
    )


def downgrade():
    op.drop_column(table_name="file", column_name="file_type")

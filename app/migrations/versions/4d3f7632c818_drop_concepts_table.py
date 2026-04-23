"""drop concepts table

Revision ID: 4d3f7632c818
Revises: 5bdd87c3040c
Create Date: 2026-04-23 19:11:12.059085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d3f7632c818'
down_revision: Union[str, Sequence[str], None] = '5bdd87c3040c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('concepts')


def downgrade():
    op.create_table(
        'concepts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('patent_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['patent_id'], ['patents.id'])
    )

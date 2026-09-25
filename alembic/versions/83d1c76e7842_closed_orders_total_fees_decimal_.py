"""closed_orders total_fees decimal precision

Revision ID: 83d1c76e7842
Revises: 4fb723179d18
Create Date: 2026-09-25 09:18:59.923196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '83d1c76e7842'
down_revision: Union[str, Sequence[str], None] = '4fb723179d18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('closed_orders', schema=None) as batch_op:
        batch_op.alter_column('total_fees',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=10, scale=3),
               existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('closed_orders', schema=None) as batch_op:
        batch_op.alter_column('total_fees',
               existing_type=sa.Numeric(precision=10, scale=3),
               type_=sa.INTEGER(),
               existing_nullable=False)

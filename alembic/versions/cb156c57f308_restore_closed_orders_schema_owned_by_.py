"""restore closed_orders schema owned by alembic

A tabela closed_orders e propriedade do Alembic: o model Django correspondente
(source/dashboard/models.py) tem managed = False, portanto o Django nao deve
gerenciar o schema desta tabela.

O que aconteceu: o Django rodou as migracoes 0002/0003 do app dashboard, que no
SQLite usam _remake_table (CREATE new__closed_orders -> INSERT SELECT -> DROP ->
RENAME). Essas migracoes foram escritas sobre um model desatualizado, entao a
tabela foi recriada apenas com as tres colunas que o model Django conhecia
(order_id, profit, closed_at), derrubando user_id e total_fees. O closed_at
acabou preenchido com a string literal 'created_at' pelo auto_now_add.

Esta revisao reconstroi a tabela com o schema do Base.metadata
(source/websockets/models.py) e repovoa user_id, total_fees e closed_at a partir
do dump forense recuperado das paginas livres do SQLite.

Revision ID: cb156c57f308
Revises: 83d1c76e7842
Create Date: 2026-10-04 01:16:21.671367

"""
import json
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb156c57f308'
down_revision: Union[str, Sequence[str], None] = '83d1c76e7842'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                    "closed_orders_recuperado.json")


def upgrade() -> None:
    bind = op.get_bind()

    # 1) snapshot do que sobreviveu na tabela viva (order_id + profit)
    alive = {
        row[0]: row[1]
        for row in bind.execute(sa.text("SELECT order_id, profit FROM closed_orders"))
    }

    # 2) dump forense: user_id, total_fees e closed_at reais
    recovered = {}
    with open(DUMP, encoding="utf8") as fh:
        for rec in json.load(fh):
            recovered[rec["order_id"]] = rec

    # 3) alinha a tabela ao Base.metadata: colunas perdidas + tipos/nullability
    with op.batch_alter_table("closed_orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.add_column(
            sa.Column("total_fees", sa.Numeric(precision=10, scale=3), nullable=True)
        )
        batch_op.alter_column(
            "profit",
            existing_type=sa.INTEGER(),
            type_=sa.Numeric(precision=10, scale=3),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "closed_at",
            existing_type=sa.DATETIME(),
            nullable=True,
        )

    # 4) backfill com os valores reais recuperados das paginas livres
    rows = [
        {
            "order_id": oid,
            "user_id": rec["user_id"],
            "profit": rec["profit"] if rec["profit"] is not None else alive.get(oid, 0),
            "total_fees": rec["total_fees"] if rec["total_fees"] is not None else 0,
            "closed_at": rec["closed_at"],
        }
        for oid, rec in recovered.items()
    ]

    if rows:
        bind.execute(
            sa.text(
                "UPDATE closed_orders "
                "SET user_id = :user_id, total_fees = :total_fees, "
                "closed_at = :closed_at, profit = :profit "
                "WHERE order_id = :order_id"
            ),
            rows,
        )

    # 5) fecha o schema: colunas NOT NULL, conforme Base.metadata
    with op.batch_alter_table("closed_orders", schema=None) as batch_op:
        batch_op.alter_column(
            "user_id", existing_type=sa.String(length=36), nullable=False
        )
        batch_op.alter_column(
            "total_fees",
            existing_type=sa.Numeric(precision=10, scale=3),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("closed_orders", schema=None) as batch_op:
        batch_op.drop_column("total_fees")
        batch_op.drop_column("user_id")
        batch_op.alter_column(
            "profit",
            existing_type=sa.Numeric(precision=10, scale=3),
            type_=sa.INTEGER(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "closed_at",
            existing_type=sa.DATETIME(),
            nullable=False,
        )

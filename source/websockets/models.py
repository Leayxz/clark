from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class ClosedOrder(Base):

    __tablename__ = "closed_orders"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    profit: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    total_fees: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=0)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

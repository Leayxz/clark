from sqlalchemy import DateTime, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from datetime import datetime
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class ClosedOrder(Base):
    """
    - Tabela responsável pelos dados de venda de cada ordem dos usuários.
    - Atributos:
        - order_id: str
        - profit: int
        - closed_at: datetime
    """

    __tablename__ = "closed_orders"

    order_id: Mapped[str] = mapped_column(String, primary_key=True)
    profit: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    closed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


engine = create_async_engine("sqlite+aiosqlite:///sqlite.db", echo=False)
SessionLocal = async_sessionmaker(bind=engine)

import pytest, pytest_asyncio, uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import select

from ..dtos import AllOpenOrdersDTO, ConfigurationDTO, CredentialsDTO, SellOrderDTO
from .models import ClosedOrder, Base
from .repository import AutomationExecutorRepository
from .service import AutomationExecutor
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
SessionLocal = async_sessionmaker(bind=engine)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    # Cria todas as tabelas registradas no Base na memória
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_save_closed_order():

    user_id = uuid.uuid7()
    sold_order = SellOrderDTO(
        order_id="order-456",
        exit_price=Decimal("65000"),
        margin_used=Decimal("100"),
        profit=Decimal("100.50"),
        total_fees=Decimal("250"),
        closed_at=datetime.now(timezone.utc)
    )
    repository = AutomationExecutorRepository(MagicMock(), SessionLocal, MagicMock())
    await repository.save_closed_order(user_id=str(user_id), sold_order=sold_order)

    async with SessionLocal() as session:
        result = await session.execute(select(ClosedOrder).where(ClosedOrder.order_id == "order-456"))

        order = result.scalar_one()

    assert order.user_id == str(user_id)
    assert order.order_id == "order-456"
    assert order.profit == Decimal("100.50")
    assert order.total_fees == Decimal("250")


def _make_credentials_dto(exchange: str = "lnmarkets") -> CredentialsDTO:
    return CredentialsDTO(
        API_KEY="key-123",
        API_SECRET="secret-456",
        API_PASSPHRASE=None,
        EXCHANGE=exchange,
    )


@pytest.mark.asyncio
async def test_get_requirements_exchange_match():
    """Credenciais com EXCHANGE igual à exchange solicitada: não levanta AssertionError."""
    user_id = uuid.uuid7()
    cache_client = AsyncMock()
    # hgetall para credenciais
    cache_client.hgetall.side_effect = [
        {
            "API_KEY": "key-123",
            "API_SECRET": "secret-456",
            "EXCHANGE": "lnmarkets",
        },
        {
            "wallet_balance": "1000",
            "marginUSD": "100",
            "leverage": "5",
            "percentage_profit": "50",
            "buy_variation": "200",
            "last_buy_up": "65000",
            "last_buy_down": "63000",
        },
    ]

    repository = AutomationExecutorRepository(cache_client, SessionLocal, MagicMock())
    credentials, configuration = await repository.get_requirements(user_id, "lnmarkets")

    assert credentials.EXCHANGE == "lnmarkets"
    assert configuration.exchange == "lnmarkets"


@pytest.mark.asyncio
async def test_get_requirements_exchange_mismatch_raises():
    """Credenciais com EXCHANGE diferente da solicitada: AssertionError."""
    user_id = uuid.uuid7()
    cache_client = AsyncMock()
    cache_client.hgetall.side_effect = [
        {
            "API_KEY": "key-123",
            "API_SECRET": "secret-456",
            "EXCHANGE": "hyperliquid",
        },
        {
            "wallet_balance": "1000",
            "marginUSD": "100",
            "leverage": "5",
            "percentage_profit": "50",
            "buy_variation": "200",
            "last_buy_up": "65000",
            "last_buy_down": "63000",
        },
    ]

    repository = AutomationExecutorRepository(cache_client, SessionLocal, MagicMock())

    with pytest.raises(AssertionError, match="Exchange inválida"):
        await repository.get_requirements(user_id, "lnmarkets")


@pytest.mark.asyncio
async def test_get_all_open_orders_uses_credentials_exchange():
    """get_all_open_orders deve funcionar sem parâmetro exchange e rotear pelo gateway usando credentials.EXCHANGE."""
    user_id = uuid.uuid7()
    gateway = AsyncMock()
    gateway.get_all_open_orders.return_value = ([AllOpenOrdersDTO(order_id="o-1", entry_price=Decimal("65000"))], 100.0)

    repository = AutomationExecutorRepository(AsyncMock(), SessionLocal, gateway)
    credentials = _make_credentials_dto("lnmarkets")

    all_orders, total_margin = await repository.get_all_open_orders(user_id, credentials)

    assert len(all_orders) == 1
    assert all_orders[0].order_id == "o-1"
    assert total_margin == 100.0
    gateway.get_all_open_orders.assert_awaited_once_with(credentials)

from pathlib import Path

import redis.asyncio as async_redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..constants import EXCHANGES
from .gateway import ExchangeGateway
from .interfaces import ExchangeProtocol
from .notifier import Telegram
from .providers.hyperliquid import HyperliquidClient
from .providers.lnmarkets import LNMarketsClient
from .repository import AutomationExecutorRepository, WSUserStateRepository
from .service import AutomationExecutor

DATABASE_PATH = Path(__file__).resolve().parents[2] / "sqlite.db"
engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}", echo=False)
SessionLocal = async_sessionmaker(bind=engine)

redis_client = async_redis.Redis(decode_responses=True, socket_connect_timeout=1, socket_timeout=1)

ws_repository = WSUserStateRepository(redis_client)

exchange_clients: dict[str, ExchangeProtocol] = {EXCHANGES.LNMARKETS: LNMarketsClient(), EXCHANGES.HYPERLIQUID: HyperliquidClient()}
exchange_gateway = ExchangeGateway(exchange_clients)

automation_executor_repository = AutomationExecutorRepository(redis_client, SessionLocal, exchange_gateway)
notifier_client = Telegram(automation_executor_repository)
automation_executor = AutomationExecutor(automation_executor_repository, exchange_gateway, notifier_client)

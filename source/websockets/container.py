import redis.asyncio as async_redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .repository import WSUserStateRepository, AutomationExecutorRepository
from .service import AutomationExecutor
from .gateway import ExchangeGateway
from .providers.lnmarkets import LNMarketsClient
from .providers.hyperliquid import HyperliquidClient

from .notifier import Telegram
from ..constants import EXCHANGES

engine = create_async_engine("sqlite+aiosqlite:///sqlite.db", echo=False)
SessionLocal = async_sessionmaker(bind=engine)
redis_client = async_redis.Redis(decode_responses=True)

exchange_clients = {EXCHANGES.LNMARKETS: LNMarketsClient(), EXCHANGES.HYPERLIQUID: HyperliquidClient()}
exchange_gateway = ExchangeGateway(exchange_clients)
ws_repository = WSUserStateRepository(redis_client)
automation_executor_repository = AutomationExecutorRepository(redis_client, SessionLocal, exchange_gateway)
notifier_client = Telegram(automation_executor_repository)
automation_executor = AutomationExecutor(automation_executor_repository, exchange_gateway, notifier_client)

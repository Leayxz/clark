import redis.asyncio as async_redis

from .repository import WSLNMarketsRepository, AutomationExecutorRepository
from .models import SessionLocal
from .service import AutomationExecutor
from ..notifier.repository import Telegram
from .clients.lnmarkets import LNMarketsClient


redis_client = async_redis.Redis()
exchange_client = LNMarketsClient()
notifier_client = Telegram()

ws_lnmarkets_repository = WSLNMarketsRepository(redis_client)
automation_executor_repository = AutomationExecutorRepository(redis_client, SessionLocal, exchange_client)

automation_executor = AutomationExecutor(automation_executor_repository, exchange_client, notifier_client)

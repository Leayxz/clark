import asyncio
from decimal import Decimal
from uuid import UUID

from ..constants import EXCHANGES
from ..events import AutomationEvent, Channel
from .container import automation_executor, automation_executor_repository, ws_repository
from .providers.lnmarkets import LNMarketsClient
from .repository import AutomationExecutorRepository, WSUserStateRepository
from .service import AutomationExecutor


class Price:
    USD: Decimal = Decimal("0")


async def websocket_lnmarkets(automation_executor: AutomationExecutor, repository: WSUserStateRepository, PRICE: type[Price]):

    await repository.synchronize_websocket(EXCHANGES.LNMARKETS)

    async for current_price in LNMarketsClient().subscribe_ticker():
        PRICE.USD = current_price
        for user_id, user_exchange in repository.get_all_activated_automations():
            await automation_executor.execute(user_id, current_price, user_exchange)


async def listen_enable_disable_automations(ws_repository: WSUserStateRepository, automation_executor_repository: AutomationExecutorRepository):

    async for payload in ws_repository.subscribe_channel(Channel.AUTOMATION):

        if payload["type"] == AutomationEvent.STARTED:
            ws_repository.add_activated_automation(UUID(payload.get("user_id")), str(payload.get("exchange")))


        elif payload["type"] == AutomationEvent.STOPPED:
            automation_executor_repository.clear_user_memory_state(UUID(payload.get('user_id')))
            ws_repository.remove_activated_automation(UUID(payload.get('user_id')))

async def persist_btc_usd_price(repository: WSUserStateRepository, PRICE: type[Price]):
    while True:
        await asyncio.sleep(120)
        await repository.save_btc_price(PRICE.USD)


async def main():

    await asyncio.gather(
        websocket_lnmarkets(automation_executor, ws_repository, Price),
        listen_enable_disable_automations(ws_repository, automation_executor_repository),
        persist_btc_usd_price(ws_repository, Price),
    )

asyncio.run(main())

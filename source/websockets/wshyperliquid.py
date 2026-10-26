import asyncio
from uuid import UUID

from ..constants import EXCHANGES
from ..events import AutomationEvent, Channel
from .container import automation_executor, automation_executor_repository, ws_repository
from .providers.hyperliquid import HyperliquidClient
from .repository import AutomationExecutorRepository, WSUserStateRepository
from .service import AutomationExecutor


async def websocket_hyperliquid(automation_executor: AutomationExecutor, repository: WSUserStateRepository):

    await repository.synchronize_websocket(EXCHANGES.HYPERLIQUID)

    async for current_price in HyperliquidClient().subscribe_ticker():
        for user_id, user_exchange in repository.get_all_activated_automations():
            await automation_executor.execute(user_id, current_price, user_exchange)


async def listen_enable_disable_automations(ws_repository: WSUserStateRepository,
                                            automation_executor_repository: AutomationExecutorRepository):

    async for payload in ws_repository.subscribe_channel(Channel.AUTOMATION):

        if payload["type"] == AutomationEvent.STARTED:
            ws_repository.add_activated_automation(UUID(payload.get("user_id")), str(payload.get("exchange")))

        elif payload["type"] == AutomationEvent.STOPPED:
            automation_executor_repository.clear_user_memory_state(UUID(payload.get('user_id')))
            ws_repository.remove_activated_automation(UUID(payload.get('user_id')))


async def main():
    await asyncio.gather(
        websocket_hyperliquid(automation_executor, ws_repository),
        listen_enable_disable_automations(ws_repository, automation_executor_repository),
    )


try:
    asyncio.run(main())

except Exception as error:
    print(f"❌ Exceção não tratada: {type(error).__module__}.{type(error).__name__}: {error}")

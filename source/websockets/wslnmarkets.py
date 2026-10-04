import asyncio, json, websockets, traceback

from .repository import WSUserStateRepository, AutomationExecutorRepository
from .service import AutomationExecutor
from .container import automation_executor, ws_repository, automation_executor_repository
from ..constants import EXCHANGES
from ..events import AutomationEvent, Channel


URL = "wss://stream.lnmarkets.com/v1"


async def websocket_lnmarket(automation_executor: AutomationExecutor,
                             repository: WSUserStateRepository,
                             exchange: str):

    await repository.synchronize_websocket(exchange)

    while True:

        try:
            async with websockets.connect(URL) as webscoket:

                payload = {"jsonrpc": "2.0", "id": 1, "method": "subscribe", "params": {"topics": ["futures/inverse/btc_usd/ticker"]}}
                await webscoket.send(json.dumps(payload))

                async for message in webscoket:
                    price_message = json.loads(message)

                    if price_message.get("method") == "subscription":
                        current_price = price_message["params"]["data"]["lastPrice"]
                        print(f"Price: {current_price}")

                        for user_id, user_exchange in repository.get_all_activated_automations():
                            await automation_executor.execute(user_id, current_price, user_exchange)


        except Exception as error:
            print(f"Websocket Error: {error} | Tentando reconectar em 5 segundos...")
            traceback.print_exc()
            await asyncio.sleep(5)


async def listen_enable_disable_automations(ws_repository: WSUserStateRepository,
                                            automation_executor_repository: AutomationExecutorRepository):

    async for payload in ws_repository.subscribe_channel(Channel.AUTOMATION):

        if payload["type"] == AutomationEvent.STARTED:
            ws_repository.add_activated_automation(payload["email"])


        elif payload["type"] == AutomationEvent.STOPPED:
            automation_executor_repository.clear_user_memory_state(payload['email'])
            ws_repository.remove_activated_automation(payload['email'])

async def main():


    await asyncio.gather(
        websocket_lnmarket(automation_executor, ws_repository, EXCHANGES.LNMARKETS),
        listen_enable_disable_automations(ws_repository, automation_executor_repository)
    )

asyncio.run(main())

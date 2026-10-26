import asyncio, json, traceback
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import websockets
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

from ...dtos import AllOpenOrdersDTO, BuyOrderDTO, ConfigurationDTO, CredentialsDTO, SellOrderDTO
from ...telemetry.logging import logger
from ...telemetry.tracing import tracer
from ..interfaces import ExchangeProtocol


class HyperliquidClient(ExchangeProtocol):

    URL = "wss://api.hyperliquid.xyz/ws"

    def __init__(self) -> None:
        self._info = Info(constants.MAINNET_API_URL, skip_ws=True)


    async def subscribe_ticker(self) -> AsyncIterator[Decimal]:

        while True:

            try:
                async with websockets.connect(self.URL) as websocket:
                    subscribe_payload = {"method": "subscribe", "subscription": {"type": "trades", "coin": "BTC"}}
                    await websocket.send(json.dumps(subscribe_payload))

                    async for message in websocket:
                        if json.loads(message).get("channel") == "subscriptionResponse": continue
                        current_price = json.loads(message).get("data")[0].get("px")
                        print(f"🟢 Price: {current_price}")
                        yield Decimal(str(current_price))

            except Exception as error:
                print(f"Websocket Error: {error} | Tentando reconectar em 5 segundos...")
                traceback.print_exc()
                await asyncio.sleep(5)


    async def open_purchase_order(self, user_id: UUID, credentials: CredentialsDTO, configuration: ConfigurationDTO) -> BuyOrderDTO:

        with tracer.start_as_current_span("clients.hyperliquid.open_purchase_order"):
            wallet = Account.from_key(credentials.API_SECRET)
            exchange = Exchange(wallet, constants.MAINNET_API_URL)
            coin = "BTC"

            # 1. Configure leverage + isolated
            await exchange.update_leverage(configuration.leverage, coin, False)

            # 2. Buy based on USD margin
            price = float(self._info.all_mids()[coin])
            size = float(configuration.marginUSD) / price

            logger.info(f"Comprando {size:.8f} {coin} a ${price:.2f}", extra={"user_id": user_id})

            result = await exchange.market_open(
                coin,
                True,       # BUY
                size,
                None,       # None = market
                0.01        # 1% slippage
            )

            return BuyOrderDTO(
                order_id=result["oid"],
                entry_price=Decimal(str(result["avgPx"])),
                margin_used=Decimal(str(configuration.marginUSD))
            )


    async def close_profitable_orders(self, user_id: UUID, credentials: CredentialsDTO, order_id: str) -> SellOrderDTO:

        with tracer.start_as_current_span("clients.hyperliquid.close_profitable_orders"):
            wallet = Account.from_key(credentials.API_SECRET)
            exchange = Exchange(wallet, constants.MAINNET_API_URL)
            coin = "BTC"

            result = await exchange.cancel(coin, int(order_id))

            print("Ordem fechada com sucesso")

            return SellOrderDTO(
                order_id=order_id,
                exit_price=Decimal(str(result.get("avgPx", 0))),
                margin_used=Decimal(str(result.get("marginUsed", 0))),
                profit=Decimal(str(result.get("pl", 0))),
                total_fees=Decimal(str(result.get("fees", 0))),
                closed_at=datetime.now(timezone.utc),
            )


    async def get_current_wallet_balance(self, credentials: CredentialsDTO) -> Decimal:

        assert credentials.API_KEY, "ApiKey não encontrada."

        with tracer.start_as_current_span("clients.hyperliquid.get_current_wallet_balance"):
            user_state = self._info.user_state(credentials.API_KEY)
            account_value = user_state.get("marginSummary", {}).get("accountValue", "0")
            return Decimal(str(account_value))


    async def get_all_open_orders(self, credentials: CredentialsDTO) -> tuple[list[AllOpenOrdersDTO | BuyOrderDTO], int]:

        assert credentials.API_KEY, "ApiKey não encontrada."


        with tracer.start_as_current_span("clients.hyperliquid.get_all_open_orders"):
            orders = self._info.open_orders(credentials.API_KEY)
            positions: list[AllOpenOrdersDTO | BuyOrderDTO] = []
            total_margin_used = 0.0

            for order in orders:
                entry_price = Decimal(str(order.get("px", 0)))
                margin = Decimal(str(order.get("margin", 0)))
                total_margin_used += float(margin)
                positions.append(AllOpenOrdersDTO(
                    order_id=order.get("oid", ""),
                    entry_price=entry_price
                ))

            print(f"Ordens abertas buscadas: {len(positions)}")
            return positions, int(total_margin_used)

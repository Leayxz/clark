import json, redis.asyncio as async_redis
from typing import cast
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import ClosedOrder
from .gateway import ExchangeGateway

from ..constants import CacheKeys
from ..dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrdersDTO, BuyOrderDTO, SellOrderDTO
from ..telemetry.tracing import tracer
from ..telemetry.logging import logger


class AutomationExecutorRepository:

    def __init__(self,
                 cache_client: async_redis.Redis,
                 database_client: async_sessionmaker[AsyncSession],
                 exchange_gateway: ExchangeGateway) -> None:
                self._database_client = database_client
                self._cache_client = cache_client
                self._exchange_gateway = exchange_gateway
                self._all_running_open_orders: dict[UUID, list[AllOpenOrdersDTO | BuyOrderDTO]] = {}
                self._synchronized_references: dict[UUID, bool] = {}
                self._all_running_credentials: dict[UUID, CredentialsDTO] = {}
                self._all_running_configuration: dict[UUID, ConfigurationDTO] = {}


    def add_buy_order(self, user_id: UUID, new_order: BuyOrderDTO):
        self._all_running_open_orders.get(user_id, []).append(new_order)


    async def get_requirements(self, user_id: UUID, exchange: str) -> tuple[CredentialsDTO, ConfigurationDTO]:

        credentials = self._all_running_credentials.get(user_id, None)
        configuration = self._all_running_configuration.get(user_id, None)

        if not credentials or not configuration:
            credentials_raw: dict = await self._cache_client.hgetall(f"{CacheKeys.AUTOMATION_CREDENTIALS}:{exchange}:{user_id}")
            assert credentials_raw, f"Credenciais de API não encontradas | exchange={exchange} | Usuário: {user_id}."
            credentials = CredentialsDTO(**credentials_raw)
            assert credentials.EXCHANGE == exchange, (
                f"Exchange inválida: esperada={exchange}, "
                f"recebida={credentials.EXCHANGE}"
            )
            self._all_running_credentials[user_id] = credentials

            configuration_raw: dict = await self._cache_client.hgetall(f"{CacheKeys.AUTOMATION_CONFIGURATION}:{exchange}:{user_id}")
            configuration = self._parse_configuration(configuration_raw, credentials)
            self._all_running_configuration[user_id] = configuration

        return credentials, configuration


    def _parse_configuration(self, configuration: dict[str, str], credentials: CredentialsDTO) -> ConfigurationDTO:

        payload = {
            "wallet_balance": Decimal(configuration.get('wallet_balance', "0")),
            "marginUSD": int(configuration.get('marginUSD', 0)),
            "leverage": int(configuration.get('leverage', 0)),
            "percentage_profit": Decimal(configuration.get('percentage_profit', "0")) / Decimal("100"),
            "buy_variation": Decimal(configuration.get('buy_variation', "0")),
            "last_buy_up": Decimal(configuration.get('last_buy_up', "0")),
            "last_buy_down": Decimal(configuration.get('last_buy_down', "0")),
            "exchange": credentials.EXCHANGE,
        }

        return ConfigurationDTO(**payload)


    async def get_all_open_orders(self, user_id: UUID, credentials: CredentialsDTO) -> tuple[list[AllOpenOrdersDTO | BuyOrderDTO], float]:
        
        all_open_orders = self._all_running_open_orders.get(user_id, None)
        total_margin_used = None

        if not all_open_orders:
            all_open_orders, total_margin_used = await self._exchange_gateway.get_all_open_orders(credentials)
            await self._cache_client.hset(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", mapping={"total_margin_used": total_margin_used, "open_orders_count": len(all_open_orders)})
            self._all_running_open_orders[user_id] = all_open_orders
            print(f"TODAS AS ORDENS ABERTAS E TOTAL MARGEM USADA BUSCADOS COM SUCESSO: {len(all_open_orders)} | {total_margin_used}")

        if not self._synchronized_references.get(user_id) or False:
            self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_up = max(order.entry_price for order in all_open_orders)
            self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_down = min(order.entry_price for order in all_open_orders)
            self._synchronized_references[user_id] = True
            print(f"REFS SINCRONIZADAS COM SUCESSO: {self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_up} | {self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_down}")

        return all_open_orders, total_margin_used if total_margin_used else 0


    async def save_closed_order(self, user_id: str, sold_order: SellOrderDTO) -> None:

        with tracer.start_as_current_span("repository.save_closed_order"):

            try:
                async with self._database_client.begin() as session:
                    session.add(ClosedOrder(user_id=str(user_id), order_id=sold_order.order_id, profit=sold_order.profit, total_fees=sold_order.total_fees, closed_at=sold_order.closed_at))

                logger.info("💾 Ordem vendida com sucesso", extra={"user_id": user_id,
                                                                   "order_id": sold_order.order_id,
                                                                   "profit": str(sold_order.profit),
                                                                   "total_fees": str(sold_order.total_fees),
                                                                   "closed_at": sold_order.closed_at})

            except Exception as exc:
                logger.error("Falha ao persistir ClosedOrder", extra={"error": str(exc)}, exc_info=True)


    def update_last_buy(self, user_id: UUID, entry_price: Decimal, BUY_UP: bool):
        if BUY_UP:
            self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_up = entry_price
            print(f"ATUALIZANDO REF BUY UP: {self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_up}")
        else:
            self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_down = entry_price
            print(f"ATUALIZANDO REF DOWN: {self._all_running_configuration.get(user_id, ConfigurationDTO()).last_buy_down}")


    def update_wallet_balance(self, user_id: UUID, margin_used: Decimal, net_profit: Decimal = Decimal("0"), BUY: bool = False):

        if BUY:
            self._all_running_configuration.get(user_id, ConfigurationDTO()).wallet_balance -= margin_used
        else:
            self._all_running_configuration.get(user_id, ConfigurationDTO()).wallet_balance += margin_used
            self._all_running_configuration.get(user_id, ConfigurationDTO()).wallet_balance += net_profit
            print(f"NOVA VENDA EXECUTADA!!")
            print(f"ADICIONANDO A CARTEIRA | MARGEM: {margin_used} | PROFIT: {net_profit}")


    async def update_dashboard_overview(self, user_id: UUID, margin_used: Decimal, BUY: bool):
        if BUY:
            await self._cache_client.hincrby(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_TOTAL_MARGIN_USED, int(margin_used))
            await self._cache_client.hincrby(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_OPEN_ORDERS_COUNT, 1)
        else:
            await self._cache_client.hincrby(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_TOTAL_MARGIN_USED, int(-margin_used))
            await self._cache_client.hincrby(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_OPEN_ORDERS_COUNT, -1)


    async def update_total_patrimony(self, user_id: UUID, total_patrimony: Decimal) -> None:
        await self._cache_client.hset(f"{CacheKeys.TOTAL_PATRIMONY}:{user_id}", mapping={"total_patrimony": str(total_patrimony)})


    def remove_sold_order(self, user_id: UUID, order_id: str):
        
        orders = self._all_running_open_orders.get(user_id, [])

        for order in orders:
            if order_id == order.order_id:
                orders.remove(order)
                return


    def clear_user_memory_state(self, user_id: UUID):
        self._all_running_credentials.pop(user_id, None)
        self._all_running_configuration.pop(user_id, None)
        self._all_running_open_orders.pop(user_id, None)
        self._synchronized_references.pop(user_id)
        print(f"REMOVENDO CREDENCIAIS")
        print(f"REMOVENDO CONFIGURATION")
        print(f"REMOVENDO ORDENS ABERTAS")
        print(f"REMOVENDO SINCRONIZAÇÂO")
        print(f"REMOÇÃO COMPLETA USER: {user_id}")



class WSUserStateRepository:
    """Repositório de estado em memória para automações websocket, generalizado por exchange."""

    def __init__(self, cache_client: async_redis.Redis) -> None:
        self._cache_client = cache_client
        self._all_activated_automations: list[tuple[UUID, str]] = []  # (user_id, exchange)

    def add_activated_automation(self, user_id: UUID, exchange: str) -> None:
        self._all_activated_automations.append((user_id, exchange))

    def get_all_activated_automations(self) -> list[tuple[UUID, str]]:
        return self._all_activated_automations

    async def synchronize_websocket(self, exchange: str) -> None:
        automations = await self._cache_client.smembers(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}")
        self._all_activated_automations = [
            (UUID(json.loads(automation)['user_id']), json.loads(automation)['exchange'])
            for automation in automations
            if json.loads(automation).get('exchange') == exchange
        ]

    async def subscribe_channel(self, channel: str) -> AsyncIterator[dict]:
        pubsub = self._cache_client.pubsub()
        await pubsub.subscribe(channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])

    def remove_activated_automation(self, user_id: UUID):
        self._all_activated_automations = [
            (uid, ex) for uid, ex in self._all_activated_automations if uid != user_id
        ]

    async def save_btc_price(self, btc_usd_price: int):
        await self._cache_client.set("BTC_USD_PRICE", int(btc_usd_price))
        print(f"SALVANDO PREÇO BTC USD")

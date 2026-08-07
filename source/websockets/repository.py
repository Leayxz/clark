import json, redis.asyncio as async_redis
from typing import cast
from decimal import Decimal
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from .models import ClosedOrder
from .interfaces import ExchangeProtocol

from ..constants import CacheKeys
from ..dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrders, BuyOrderDTO
from ..constants import CacheKeys


class AutomationExecutorRepository:

    def __init__(self,
                 cache_client: async_redis.Redis,
                 database_client: async_sessionmaker[AsyncSession],
                 exchange_client: ExchangeProtocol) -> None:

                self._database_client = database_client
                self._cache_client = cache_client
                self._exchange_client = exchange_client
                self._all_running_open_orders: dict[str, list[AllOpenOrders | BuyOrderDTO]] = {}
                self._synchronized_references: dict[str, bool] = {}
                self._all_running_credentials: dict[str, CredentialsDTO] = {}
                self._all_running_configuration: dict[str, ConfigurationDTO] = {}


    def add_buy_order(self, email: str, new_order: BuyOrderDTO):
        self._all_running_open_orders.get(email, []).append(new_order)
        print(f"Adicionando nova ordem na lista.")


    async def get_credentials(self, email) -> CredentialsDTO:
        credentials = self._all_running_credentials.get(email, None)
        if not credentials:
            credentials = cast(bytes, await self._cache_client.get(f"{CacheKeys.LNMCREDENTIALS}:{email}"))
            credentials = CredentialsDTO(**json.loads(credentials))
            self._all_running_credentials[email] = credentials

        return credentials


    async def get_configuration(self, email: str, credentials: CredentialsDTO) -> ConfigurationDTO:
        configuration = self._all_running_configuration.get(email, None)
        
        if not configuration:
            bytes_config = cast(bytes | None, await self._cache_client.get(f"{CacheKeys.LNMCONFIGURATION}:{email}"))
            if not bytes_config: return ConfigurationDTO()
            dict_config = json.loads(bytes_config)
            
            payload = {
                "wallet_balance": Decimal(dict_config['wallet_balance']),
                "marginUSD": dict_config['marginUSD'],
                "leverage": dict_config['leverage'],
                "percentage_profit": Decimal(dict_config['percentage_profit']) / Decimal("100"), # divisão para 0.005%
                "buy_variation": Decimal(dict_config['buy_variation']),
                "last_buy_up": Decimal(dict_config['last_buy_up']),
                "last_buy_down": Decimal(dict_config['last_buy_down'])
            }        

            configuration = ConfigurationDTO(**payload)
            self._all_running_configuration[email] = configuration

        if not configuration.wallet_balance:
            wallet_balance = await self._exchange_client.get_current_wallet_balance(credentials)
            self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance = wallet_balance

        return configuration


    async def get_all_open_orders(self, email: str, credentials: CredentialsDTO) -> list[AllOpenOrders | BuyOrderDTO]:
        all_open_orders = self._all_running_open_orders.get(email, None)

        if not all_open_orders:
            all_open_orders = await self._exchange_client.get_all_open_orders(credentials)

        if not self._synchronized_references.get(email):
            self._all_running_open_orders[email] = all_open_orders
            self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_up = max(order.entry_price for order in all_open_orders)
            self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_down = min(order.entry_price for order in all_open_orders)
            self._synchronized_references[email] = True
            print(f"Refs sincronizadas com sucesso | Ref Subindo: {self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_up} | Ref Descendo: {self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_down}")

        return all_open_orders


    async def save_closed_order(self, order_id: str, profit: Decimal) -> None:
        async with self._database_client.begin() as session:
            session.add(ClosedOrder(order_id=order_id, profit=profit))
        print("Nova venda salva em DB com sucesso.")


    def update_last_buy_up(self, email: str, entry_price: Decimal):
        self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_up = entry_price
        print(f"Atualizando Ref Subindo: {self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_up}")


    def update_last_buy_down(self, email: str, entry_price: Decimal):
        self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_down = entry_price
        print(f"Atualizando Ref Descendo: {self._all_running_configuration.get(email, ConfigurationDTO()).last_buy_down}")


    def update_wallet_balance_buy(self, email: str, margin_used: Decimal):
        print(f"Atualizando SaldoWallet: {self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance}")
        print(f"Removendo: {margin_used}")
        self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance -= margin_used
        print(f"Saldo Atual: {self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance}")


    def update_wallet_balance_sale(self, email: str, margin_used: Decimal, net_profit: Decimal):
        self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance += margin_used
        self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance += net_profit
        print(f"Atualizando SaldoWallet | Adicionando: {margin_used} | WalletAtual: {self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance}")
        print(f"Atualizando SaldoWallet | Adicionando: {net_profit} | WalletAtual: {self._all_running_configuration.get(email, ConfigurationDTO()).wallet_balance}")


    def remove_sold_order(self, email: str, order_id: str):
        orders = self._all_running_open_orders.get(email, [])

        for order in orders:
            if order_id == order.order_id:
                orders.remove(order)
                print(f"Removido ordem vendida da lista usando ID | Ordem vendida: {order_id} | Ordem removida: {order.order_id}")
                return


    def clear_user_memory_state(self, email: str):
        self._all_running_credentials.pop(email, None)
        self._all_running_configuration.pop(email, None)
        self._all_running_open_orders.pop(email, None)
        self._synchronized_references.pop(email)
        print(f"Removendo credenciais: {self._all_running_credentials}")
        print(f"Removendo configuração: {self._all_running_configuration}")
        print(f"Removendo ordens abertas: {self._all_running_open_orders}")
        print(f"Removendo estado de sincronização: {self._synchronized_references}")


class WSLNMarketsRepository:

    def __init__(self,
                 cache_client: async_redis.Redis) -> None:

                self._cache_client = cache_client
                self._all_activated_automations: list[str] = []


    def add_activated_automation(self, email: str) -> None:
        self._all_activated_automations.append(email)
        print(f"Adicionando usuário para rodar na automação: {email}")


    def get_all_activated_automations(self) -> list[str]:
        return self._all_activated_automations


    async def synchronize_websocket(self,) -> None:
        automations = cast(str, await self._cache_client.smembers(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}"))
        all_activated_automations = [json.loads(automation)['email'] for automation in automations]
        self._all_activated_automations = all_activated_automations
        print(f"TODAS AS AUTOMAÇÔES ATIVAS: {all_activated_automations}")


    async def subscribe_channel(self, channel: str) -> AsyncIterator[dict]:
        pubsub = self._cache_client.pubsub()
        await pubsub.subscribe(channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])


    def remove_activated_automation(self, email: str):
        self._all_activated_automations.remove(email)
        print(f"Removendo Automação | User: {email}")

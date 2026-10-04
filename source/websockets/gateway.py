from uuid import UUID
from decimal import Decimal

from .interfaces import ExchangeProtocol
from ..dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrdersDTO, BuyOrderDTO, SellOrderDTO


class ExchangeGateway:

    def __init__(self, exchange_clients: dict[str, ExchangeProtocol]) -> None:
        self._exchange_clients = exchange_clients

    async def open_purchase_order(self, user_id: UUID, credentials: CredentialsDTO, configuration: ConfigurationDTO) -> BuyOrderDTO:
        assert credentials.EXCHANGE, "credentials.EXCHANGE não preenchido"
        client = self._exchange_clients.get(credentials.EXCHANGE)
        assert client, f"Exchange client não encontrado para: {credentials.EXCHANGE}"
        return await client.open_purchase_order(user_id, credentials, configuration)

    async def close_profitable_orders(self, user_id: UUID, credentials: CredentialsDTO, order_id: str) -> SellOrderDTO:
        assert credentials.EXCHANGE, "credentials.EXCHANGE não preenchido"
        client = self._exchange_clients.get(credentials.EXCHANGE)
        assert client, f"Exchange client não encontrado para: {credentials.EXCHANGE}"
        return await client.close_profitable_orders(user_id, credentials, order_id)

    async def get_current_wallet_balance(self, credentials: CredentialsDTO) -> Decimal:
        assert credentials.EXCHANGE, "credentials.EXCHANGE não preenchido"
        client = self._exchange_clients.get(credentials.EXCHANGE)
        assert client, f"Exchange client não encontrado para: {credentials.EXCHANGE}"
        return await client.get_current_wallet_balance(credentials)

    async def get_all_open_orders(self, credentials: CredentialsDTO) -> tuple[list[AllOpenOrdersDTO | BuyOrderDTO], float]:
        assert credentials.EXCHANGE, "credentials.EXCHANGE não preenchido"
        client = self._exchange_clients.get(credentials.EXCHANGE)
        assert client, f"Exchange client não encontrado para: {credentials.EXCHANGE}"
        return await client.get_all_open_orders(credentials)

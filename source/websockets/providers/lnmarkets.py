from lnmarkets_sdk.rest.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.rest.v3.models.futures_isolated import FuturesOrder, CloseTradeParams

from decimal import Decimal
from datetime import datetime

from ..interfaces import ExchangeProtocol
from ...dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrdersDTO, BuyOrderDTO, SellOrderDTO
from ...telemetry.tracing import tracer
from ...telemetry.logging import logger
from uuid import UUID

class LNMarketsClient(ExchangeProtocol):

    async def open_purchase_order(self, user_id: UUID, credentials:CredentialsDTO, configuration:ConfigurationDTO) -> BuyOrderDTO:

        assert credentials.API_KEY, f"API_KEY NÃO ENCONTRADA."
        assert credentials.API_PASSPHRASE, f"API_PASSPHRASE NÃO ENCONTRADA."
        assert credentials.API_SECRET, f"API_SECRET NÃO ENCONTRADA."

        authentication = APIAuthContext(key=credentials.API_KEY, secret=credentials.API_SECRET, passphrase=credentials.API_PASSPHRASE)
        client_config = APIClientConfig(authentication=authentication, network="mainnet")

        async with LNMClient(client_config) as client:
            order = FuturesOrder(type="market", side="buy", quantity=configuration.marginUSD, leverage=configuration.leverage)
            new_order = await client.futures.isolated.new_trade(order)

            logger.info(f"💵 Nova ordem comprada com sucesso: {new_order.entry_price}", extra={"user_id": user_id})
            # preciso de log de erro caso algo falhe para a lnmarkets

            return BuyOrderDTO(order_id=new_order.id,
                               entry_price=Decimal(str(new_order.entry_price)),
                               margin_used=Decimal(str(new_order.margin)))


    async def close_profitable_orders(self, user_id: UUID, credentials:CredentialsDTO, order_id: str) -> SellOrderDTO:

        assert credentials.API_KEY, f"API_KEY NÃO ENCONTRADA."
        assert credentials.API_PASSPHRASE, f"API_PASSPHRASE NÃO ENCONTRADA."
        assert credentials.API_SECRET, f"API_SECRET NÃO ENCONTRADA."

        with tracer.start_as_current_span("clients.lnmarkets.close_profitable_orders"):

            authentication = APIAuthContext(key=credentials.API_KEY, secret=credentials.API_SECRET, passphrase=credentials.API_PASSPHRASE)
            client_config = APIClientConfig(authentication=authentication, network="mainnet")

            async with LNMClient(client_config) as client:
                ordem_fechamento = CloseTradeParams(id=order_id)
                fechamento = await client.futures.isolated.close(ordem_fechamento)

                logger.info(f"💰 Ordem fechada com sucesso", extra={
                    "user_id": user_id,
                    "lucro_liquido": fechamento.pl - (fechamento.opening_fee + fechamento.closing_fee + fechamento.sum_funding_fees),
                    "opening_fee": fechamento.opening_fee,
                    "closing_fee": fechamento.closing_fee,
                    "sum_funding_fees": fechamento.sum_funding_fees
                })


        return SellOrderDTO(order_id=fechamento.id,
                            margin_used=Decimal(str(fechamento.margin)),
                            profit=Decimal(str(fechamento.pl - (fechamento.opening_fee + fechamento.closing_fee + fechamento.sum_funding_fees))),
                            total_fees=Decimal(str(fechamento.opening_fee + fechamento.closing_fee + fechamento.sum_funding_fees)),
                            exit_price=Decimal(str(fechamento.exit_price)),
                            closed_at=datetime.fromisoformat(fechamento.created_at.replace('Z', '+00:00')))


    async def get_current_wallet_balance(self, credentials: CredentialsDTO) -> Decimal:

        assert credentials.API_KEY, f"API_KEY NÃO ENCONTRADA."
        assert credentials.API_PASSPHRASE, f"API_PASSPHRASE NÃO ENCONTRADA."
        assert credentials.API_SECRET, f"API_SECRET NÃO ENCONTRADA."

        with tracer.start_as_current_span("clients.lnmarkets.get_current_wallet_balance"):

            authentication = APIAuthContext(key=credentials.API_KEY, secret=credentials.API_SECRET, passphrase=credentials.API_PASSPHRASE)
            client_config = APIClientConfig(authentication=authentication, network="mainnet")

            async with LNMClient(client_config) as client:
                wallet_balance = await client.account.get_account()

        return Decimal(f"{wallet_balance.balance}")


    async def get_all_open_orders(self, credentials: CredentialsDTO) -> tuple[list[AllOpenOrdersDTO | BuyOrderDTO], float]:

        assert credentials.API_KEY, f"API_KEY NÃO ENCONTRADA."
        assert credentials.API_PASSPHRASE, f"API_PASSPHRASE NÃO ENCONTRADA."
        assert credentials.API_SECRET, f"API_SECRET NÃO ENCONTRADA."

        positions: list[AllOpenOrdersDTO | BuyOrderDTO] = []
        total_margin_used = 0

        authentication = APIAuthContext(key=credentials.API_KEY, secret=credentials.API_SECRET, passphrase=credentials.API_PASSPHRASE)
        client_config = APIClientConfig(authentication=authentication, network="mainnet")

        async with LNMClient(client_config) as client:
            ordens_abertas = await client.futures.isolated.get_running_trades()
            for ordem in ordens_abertas:
                total_margin_used += (ordem.margin + ordem.opening_fee)
                positions.append(AllOpenOrdersDTO(order_id=ordem.id,
                                               entry_price=Decimal(str(ordem.entry_price))))

            return positions, total_margin_used

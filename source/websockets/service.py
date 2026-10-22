from decimal import Decimal
from uuid import UUID

from ..dtos import AllOpenOrdersDTO, BuyOrderDTO, ConfigurationDTO, CredentialsDTO
from ..telemetry.logging import logger
from .gateway import ExchangeGateway
from .interfaces import AutomationExecutorProtocol, NotifierProtocol


class Regras:
    FIXED_RATE: Decimal = Decimal("0.002") # 0.2%


class AutomationExecutor:

    def __init__(self,
                 repository: AutomationExecutorProtocol,
                 gateway: ExchangeGateway,
                 notifier: NotifierProtocol) -> None:

                 self._repository = repository
                 self._gateway = gateway
                 self._notifier = notifier


    async def execute(self, user_id: UUID, current_price: Decimal, exchange: str):

        credentials, configuration = await self._repository.get_requirements(user_id, exchange)
        all_open_orders, total_margin_used = await self._repository.get_all_open_orders(user_id, credentials)
        wallet_balance = await self._repository.get_user_wallet_balance(user_id, credentials, total_margin_used)

        await self.evaluate_purchase_condition(user_id, credentials, configuration, current_price, all_open_orders, wallet_balance)
        await self.evaluate_sell_condition(user_id, credentials, configuration, current_price, all_open_orders)


    async def evaluate_purchase_condition(self,
                                          user_id: UUID,
                                          credentials: CredentialsDTO,
                                          configuration: ConfigurationDTO,
                                          current_price: Decimal,
                                          all_open_orders: list[AllOpenOrdersDTO | BuyOrderDTO],
                                          wallet_balance: Decimal):

        new_order = None

        if current_price >= (configuration.last_buy_up + configuration.buy_variation):

            if not await self._user_should_have_margin(configuration, current_price, wallet_balance):
                return

            new_order = await self._gateway.open_purchase_order(user_id, credentials, configuration)

        elif current_price <= (configuration.last_buy_down - configuration.buy_variation):

            if not await self._user_should_have_margin(configuration, current_price, wallet_balance):
                return

            new_order = await self._gateway.open_purchase_order(user_id, credentials, configuration)

        if new_order:
            self._repository.add_buy_order(user_id, new_order)
            self._repository.update_buy_references(user_id, configuration)
            await self._repository.update_user_balance(user_id, margin_used=new_order.margin_used, BUY=True)
            await self._repository.update_dashboard_overview(user_id, True)
            await self._notifier.send_buy_message(new_order.entry_price, len(all_open_orders))


    async def evaluate_sell_condition(self,
                                      user_id: UUID,
                                      credentials: CredentialsDTO,
                                      configuration: ConfigurationDTO,
                                      current_price: Decimal,
                                      all_open_orders: list[AllOpenOrdersDTO | BuyOrderDTO]):

        for order in all_open_orders.copy():

            target_price = order.entry_price * (Decimal("1") + configuration.percentage_profit + Regras.FIXED_RATE)

            if current_price >= target_price:
                sold_order = await self._gateway.close_profitable_orders(user_id, credentials, order.order_id)
                self._repository.remove_sold_order(user_id, order.order_id)
                self._repository.update_buy_references(user_id, configuration)
                await self._repository.update_user_balance(user_id, margin_used=sold_order.margin_used, profit=sold_order.profit, BUY=False)
                await self._repository.update_dashboard_overview(user_id, False)
                await self._repository.save_closed_order(user_id, sold_order)
                await self._notifier.send_sell_message(sold_order.profit, len(all_open_orders), user_id)


    async def _user_should_have_margin(self, configuration: ConfigurationDTO, current_price: Decimal, wallet_balance: Decimal) -> bool:
        margin_sats = Decimal(configuration.marginUSD) / (current_price * configuration.leverage) * 100_000_000
        logger.info(f"MARGIN SATS CALCULADO PARA SER USADO NA VERIFICAÇÂO DE MARGEM DISPONIVEL: {margin_sats}")
        return wallet_balance >= margin_sats

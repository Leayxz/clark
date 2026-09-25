from decimal import Decimal
from uuid import UUID

from .interfaces import ExchangeProtocol, NotifierProtocol, AutomationExecutorProtocol
from .gateway import ExchangeGateway
from ..dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrdersDTO, BuyOrderDTO
from ..constants import EXCHANGES


class Regras:
    SALDO_INSUFICIENTE: Decimal = Decimal("320")
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

        if not configuration.wallet_balance:
            wallet_balance = await self._gateway.get_current_wallet_balance(credentials)
            configuration.wallet_balance = wallet_balance
            await self._repository.update_total_patrimony(user_id, (Decimal(total_margin_used) + wallet_balance))

        await self.evaluate_purchase_condition(user_id, credentials, configuration, current_price)
        await self.evaluate_sell_condition(user_id, credentials, configuration, current_price, all_open_orders)


    async def evaluate_purchase_condition(self,
                                          user_id: UUID,
                                          credentials: CredentialsDTO,
                                          configuration: ConfigurationDTO,
                                          current_price: Decimal):

        if configuration.wallet_balance <= Regras.SALDO_INSUFICIENTE:
            return

        new_order = None

        if current_price >= (configuration.last_buy_up + configuration.buy_variation):
            new_order = await self._gateway.open_purchase_order(user_id, credentials, configuration)
            self._repository.update_last_buy(user_id, new_order.entry_price, BUY_UP=True)

        elif current_price <= (configuration.last_buy_down - configuration.buy_variation):
            new_order = await self._gateway.open_purchase_order(user_id, credentials, configuration)
            self._repository.update_last_buy(user_id, new_order.entry_price, BUY_UP=False)

        if new_order:
            self._repository.add_buy_order(user_id, new_order)
            self._repository.update_wallet_balance(user_id, new_order.margin_used, BUY=True)
            await self._repository.update_dashboard_overview(user_id, new_order.margin_used, True)
            await self._notifier.send_buy_message(new_order.entry_price)


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
                self._repository.update_last_buy(user_id, sold_order.exit_price, BUY_UP=False)
                self._repository.update_wallet_balance(user_id, sold_order.margin_used, sold_order.profit)
                await self._repository.update_dashboard_overview(user_id, sold_order.margin_used, False)
                await self._repository.save_closed_order(str(user_id), sold_order)
                await self._notifier.send_sell_message(sold_order.profit, len(all_open_orders))

from decimal import Decimal
from .interfaces import ExchangeProtocol, NotifierProtocol, AutomationExecutorProtocol
from ..dtos import CredentialsDTO, ConfigurationDTO, AllOpenOrders, BuyOrderDTO


class Regras:
    SALDO_INSUFICIENTE: Decimal = Decimal("320")
    FIXED_RATE: Decimal = Decimal("0.002") # 0.2%


class AutomationExecutor:

    def __init__(self,
                 repository: AutomationExecutorProtocol,
                 exchange: ExchangeProtocol,
                 notifier: NotifierProtocol) -> None:

                self._repository = repository
                self._exchange = exchange
                self._notifier = notifier


    async def execute(self, email: str, current_price: Decimal):
        credentials = await self._repository.get_credentials(email)
        configuration = await self._repository.get_configuration(email, credentials)
        all_open_orders = await self._repository.get_all_open_orders(email, credentials)

        await self.evaluate_purchase_condition(email, credentials, configuration, current_price)
        await self.evaluate_sale_condition(email, credentials, configuration, current_price, all_open_orders)


    async def evaluate_purchase_condition(self,
                                          email: str,
                                          credentials: CredentialsDTO,
                                          configuration: ConfigurationDTO,
                                          current_price: Decimal):

        if configuration.wallet_balance <= Regras.SALDO_INSUFICIENTE:
            return

        new_order = None

        if current_price >= (configuration.last_buy_up + configuration.buy_variation):
            new_order = await self._exchange.open_purchase_order(credentials, configuration)
            self._repository.update_last_buy_up(email, new_order.entry_price)


        elif current_price <= (configuration.last_buy_down - configuration.buy_variation):
            new_order = await self._exchange.open_purchase_order(credentials, configuration)
            self._repository.update_last_buy_down(email, new_order.entry_price)


        if new_order:
            self._repository.add_buy_order(email, new_order)
            self._repository.update_wallet_balance_buy(email, new_order.margin_used)
            await self._notifier.send_buy_message(new_order.entry_price)


    async def evaluate_sale_condition(self,
                                      email: str,
                                      credentials: CredentialsDTO,
                                      configuration: ConfigurationDTO,
                                      current_price: Decimal,
                                      all_open_orders: list[AllOpenOrders | BuyOrderDTO]):

        for order in all_open_orders.copy():

            target_price = order.entry_price * (Decimal("1") + configuration.percentage_profit + Regras.FIXED_RATE)

            if current_price >= target_price:
                sold_order = await self._exchange.close_profitable_orders(credentials, order.order_id)
                await self._repository.save_closed_order(sold_order.order_id, sold_order.profit)
                await self._notifier.send_sell_message(sold_order.profit)
                self._repository.remove_sold_order(email, order.order_id)
                self._repository.update_last_buy_down(email, sold_order.exit_price)
                self._repository.update_wallet_balance_sale(email, sold_order.margin_used, sold_order.profit)

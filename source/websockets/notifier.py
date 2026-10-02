import asyncio
from decimal import Decimal
from telebot import TeleBot

from .interfaces import AutomationExecutorProtocol
from ..configurations import TelegramKeys


class Telegram:

    def __init__(self, repository: AutomationExecutorProtocol) -> None:
        self._telebot = TeleBot(TelegramKeys.TELEBOT)
        self._chat_id = TelegramKeys.CHAT_ID
        self._repository = repository

    async def send_buy_message(self, entry_price: Decimal, all_open_orders: int):

        message = (
            f"🟢 Nova Compra Realizada\n\n"
            f"Entrada: {entry_price}\n"
            f"Ordens Abertas: {all_open_orders}"
        )

        await asyncio.to_thread(self._telebot.send_message, self._chat_id, message)

    async def send_sell_message(self, profit: Decimal, all_open_orders: int, user_id: str):
        
        daily = await self._repository.closed_orders_today(user_id)

        message = (
            f"🟡 Nova Ordem Vendida\n\n"
            f"Lucro Líquido: {profit}\n"
            f"Ordens Abertas: {all_open_orders}\n"
            f"💰 Ordens Fechadas Hoje: {daily}"
        )

        await asyncio.to_thread(self._telebot.send_message, self._chat_id, message)

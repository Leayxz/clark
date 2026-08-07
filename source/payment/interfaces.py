from typing import Protocol
from ..dtos import LNMarketsDTO

class PaymentProtocol(Protocol):

    def get_payment_status(self, email: str) -> bool: ...


class ProviderProtocol(Protocol):

    async def create_deposit_in_sats(self, email: str, automation_price: int) -> LNMarketsDTO: ...
    def create_deposit_in_pix(self, email: str): ...

from decimal import Decimal
from uuid import UUID

from .interfaces import DeflowExchangeProtocol
from ..dtos import DeflowExchangeDTO, PaymentDTO
from ..errors import Error


class ExchangeGateway:

    def __init__(self, provider: DeflowExchangeProtocol) -> None:
        self._provider = provider

    def create_deposit_pix(self, user_id: UUID, amount: Decimal, payment: PaymentDTO) -> DeflowExchangeDTO | Error:
        return self._provider.create_deposit_pix(user_id, amount, payment)

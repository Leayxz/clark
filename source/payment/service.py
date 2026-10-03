from uuid import UUID
from decimal import Decimal
from .interfaces import PaymentProtocol
from .gateway import ExchangeGateway
from ..constants import Automation
from ..dtos import PaymentDTO, DeflowExchangeDTO
from ..errors import Error


class PaymentService:

    def __init__(self, repository: PaymentProtocol, gateway: ExchangeGateway) -> None:
        self._repository = repository
        self._gateway = gateway

    def validate_coupon(self, coupon_code: str) -> bool:
        return self._repository.validate_coupon(coupon_code)

    def generate_payment_invoice_pix(self, user_id: UUID, payment: PaymentDTO) -> DeflowExchangeDTO | Error:

        coupon_applied = self._validate_coupon_for_discount(payment.coupon_code)
        amount_in_brl = self._apply_discount(coupon_applied)

        invoice = self._gateway.create_deposit_pix(user_id, amount_in_brl, payment)
        if isinstance(invoice, Error): return invoice

        invoice.coupon = payment.coupon_code

        rate = self._repository.get_commission_rate(payment.coupon_code)
        invoice.affiliate_commission_rate = rate
        invoice.affiliate_commission_amount = amount_in_brl * Decimal(rate) / Decimal(100)

        self._repository.save_invoice(user_id, invoice)
        self._repository.publish_event()

        return invoice

    def _validate_coupon_for_discount(self, coupon_code: str) -> bool:
        return bool(coupon_code and self._repository.validate_coupon(coupon_code))

    def _apply_discount(self, coupon_applied: bool) -> Decimal:
        amount = Automation.PRICE_IN_BRL
        if coupon_applied: amount = amount * Decimal("0.9")
        return amount

import redis, json
from uuid import UUID
from datetime import timedelta, datetime, timezone

from .interfaces import PaymentProtocol
from .models import Invoice
from source.affiliate.models import Affiliate
from ..dtos import DeflowExchangeDTO
from ..constants import PaymentStatus, AffiliateTier
from ..events import Channel, InvoiceEvent


class PaymentRepository(PaymentProtocol):

    def __init__(self, cache_client: redis.Redis) -> None:
        self._cache_client = cache_client

    def get_payment_status(self, email: str) -> bool:
        return False

    def validate_coupon(self, coupon_code: str) -> bool:
        if coupon_code == "TESTE":
            return True
        return Affiliate.objects.filter(coupon_code=coupon_code).exists()

    def get_total_active_users_with_coupon(self, coupon_code: str):
        return Invoice.objects.filter(payment_status=PaymentStatus.PAID, coupon_code=coupon_code).count()

    def get_commission_rate(self, coupon_code: str) -> int:
        paying_users = Invoice.objects.filter(
            coupon_code=coupon_code,
            payment_status__in=[PaymentStatus.PAID, PaymentStatus.PROCESSED]
        ).exclude(payment_status=PaymentStatus.REFUNDED).count()

        if paying_users >= AffiliateTier.OURO:
            return AffiliateTier.OURO
        elif paying_users >= AffiliateTier.PRATA:
            return AffiliateTier.PRATA
        return AffiliateTier.BRONZE

    def save_invoice(self, user_id: UUID, invoice: DeflowExchangeDTO) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        Invoice.objects.create(
            user_id=user_id,
            deposit_id=invoice.payment_id,
            payment_request=invoice.qr_code,
            amount_brl=invoice.amount_brl,
            payment_status=invoice.status,
            coupon_code=invoice.coupon,
            affiliate_commission_rate=invoice.affiliate_commission_rate,
            affiliate_commission_amount=invoice.affiliate_commission_amount,
            expires_at=expires_at,
        )

    def publish_event(self) -> None:
        payload = {"type": InvoiceEvent.VALIDATION}
        self._cache_client.publish(Channel.INVOICE, json.dumps(payload))

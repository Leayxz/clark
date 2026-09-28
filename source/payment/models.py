import uuid
from django.db import models
from decimal import Decimal
from ..constants import PaymentStatus


class Invoice(models.Model):
    user_id = models.UUIDField(default=uuid.uuid7, editable=False)
    deposit_id = models.CharField(max_length=30, unique=True, db_index=True)
    payment_request = models.TextField()
    payment_status = models.CharField(max_length=20, default=PaymentStatus.PENDING, db_index=True)
    coupon_code = models.CharField(max_length=15, null=True, blank=True)
    affiliate_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    affiliate_commission_amount = models.PositiveBigIntegerField(null=True, blank=True)
    amount_brl = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "invoices"

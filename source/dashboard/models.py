from decimal import Decimal
from django.db import models


class ClosedOrder(models.Model):

    user_id = models.CharField(max_length=36, db_column="user_id")
    order_id = models.CharField(primary_key=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total_fees = models.IntegerField(default=0)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "closed_orders"
        managed = False

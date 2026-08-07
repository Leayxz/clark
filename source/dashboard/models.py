from django.db import models


class ClosedOrder(models.Model):

    order_id = models.CharField(primary_key=True)
    profit = models.IntegerField()
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "closed_orders"

import uuid
from django.db import models


class Affiliate(models.Model):
    user = models.OneToOneField("authentication.User", on_delete=models.CASCADE, db_column="user_id")
    coupon_code = models.CharField(max_length=10, unique=True, null=False, db_index=True)
    liquid_address = models.CharField(max_length=100, unique=True, null=False)
    promotion_description = models.TextField(null=False, blank=False, default="")
    terms_accepted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "affiliate"

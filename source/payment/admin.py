from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("user_id", "deposit_id", "payment_status", "coupon_code", "amount_brl", "affiliate_commission_rate", "affiliate_commission_amount", "created_at")
    list_filter = ("payment_status", "created_at")
    search_fields = ("deposit_id", "user_id")
    readonly_fields = ("created_at",)
    fields = ("user_id", "deposit_id", "payment_request", "payment_status", "coupon_code", "amount_brl", "affiliate_commission_rate", "affiliate_commission_amount", "expires_at", "created_at")

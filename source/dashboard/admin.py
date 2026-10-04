from django.contrib import admin
from .models import ClosedOrder

@admin.register(ClosedOrder)
class ClosedOrderAdmin(admin.ModelAdmin):
    list_display = ("user_id", "order_id", "profit", "total_fees", "closed_at")
    search_fields = ("user_id",)
    ordering = ("-closed_at",)

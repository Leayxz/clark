from django.contrib import admin
from .models import ClosedOrder

@admin.register(ClosedOrder)
class ClosedOrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "profit", "closed_at")
    search_fields = ("order_id",)
    ordering = ("-closed_at",)

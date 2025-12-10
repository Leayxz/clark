from django.contrib import admin
from .models import InvoicesPagos

@admin.register(InvoicesPagos)
class InvoicesPagosAdmin(admin.ModelAdmin):
      list_display = ("user", "id_invoice", "timestamp", "status")

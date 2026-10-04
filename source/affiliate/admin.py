from django.contrib import admin
from .models import Affiliate


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ("user_id", "user_email", "coupon_code", "liquid_address", "created_at")
    search_fields = ("coupon_code", "liquid_address", "user__id")
    readonly_fields = ("terms_accepted_at", "created_at", "updated_at")
    ordering = ("-created_at",)

    def user_email(self, obj):
        return obj.user.email

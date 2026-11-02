from typing import Any

from rest_framework import serializers


class AffiliateRegisterSerializer(serializers.Serializer):
    liquid_address = serializers.CharField(min_length=100, max_length=110, required=True)
    coupon = serializers.CharField(min_length=5, max_length=15, required=True)
    promotion_description = serializers.CharField(min_length=100, max_length=300, required=True)

    def to_internal_value(self, data: Any) -> dict[str, str]:
        validated = super().to_internal_value(data)
        validated["liquid_address"] = validated["liquid_address"].strip()
        validated["coupon"] = validated["coupon"].strip().upper().replace(" ", "")
        validated["promotion_description"] = validated["promotion_description"].strip()
        return validated

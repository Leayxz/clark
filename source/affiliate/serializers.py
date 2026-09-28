from typing import Any
from rest_framework import serializers


class AffiliateRegisterSerializer(serializers.Serializer):
    liquid_address = serializers.CharField(min_length=20, max_length=100)
    coupon = serializers.CharField(min_length=3, max_length=10)
    promotion_description = serializers.CharField(min_length=10, max_length=300, required=True)

    def to_internal_value(self, data: Any) -> dict[str, str]:
        validated = super().to_internal_value(data)
        validated["liquid_address"] = validated["liquid_address"].strip()
        validated["coupon"] = validated["coupon"].strip().upper().replace(" ", "")
        validated["promotion_description"] = validated["promotion_description"].strip()
        return validated

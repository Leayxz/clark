import re
from rest_framework import serializers

class CouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(min_length=10, max_length=15, allow_blank=False)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data.get("coupon_code"):
            data["coupon_code"] = data["coupon_code"].strip().upper()
        return data


class PaymentSerializer(serializers.Serializer):
    # o cupom é opcional: vazio ou nulo significa pagar o valor cheio, sem desconto
    coupon_code = serializers.CharField(min_length=10, max_length=15, allow_blank=True, allow_null=True, required=False, default="")
    payer_tax_number = serializers.CharField(min_length=11, max_length=14, allow_blank=False, required=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data.get("coupon_code"):
            data["coupon_code"] = data["coupon_code"].strip().upper()
        else:
            data["coupon_code"] = ""
        if data.get("payer_tax_number"):
            data["payer_tax_number"] = re.sub(r'[^0-9]', '', data["payer_tax_number"].strip())
        return data

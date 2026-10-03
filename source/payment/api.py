from uuid import UUID
from typing import cast
from source.container import payment_service
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import CouponSerializer
from ..authentication.decorators import authenticated
from ..dtos import PaymentDTO
from ..errors import Error, ERROR_CODE_MAPPING


@api_view(["POST"])
@authenticated
def validate_coupon(request):

    serializer = CouponSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_COUPON.value}, status.HTTP_400_BAD_REQUEST)

    coupon_code = cast(dict[str, str], serializer.validated_data)["coupon_code"]
    result = payment_service.validate_coupon(coupon_code)

    if not result:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response({"coupon_code": coupon_code}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authenticated
def generate_qrcode_in_pix(request):

    serializer = CouponSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_COUPON.value}, status.HTTP_400_BAD_REQUEST)

    payment = PaymentDTO(**cast(dict[str, str], serializer.validated_data))
    result = payment_service.generate_payment_invoice_pix(UUID(request.subject), payment)

    if isinstance(result, Error):
        return Response({"error": result.value}, status=ERROR_CODE_MAPPING[result])

    return Response({"payment_id": result.payment_id,
                     "qr_code": result.qr_code,
                     "coupon": result.coupon}, status=status.HTTP_200_OK)

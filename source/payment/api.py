from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from source.container import payment_service
from ..authentication.decorators import authenticated


@api_view(["POST"])
@authenticated
def generate_qrcode_in_sats(request):
    result = async_to_sync(payment_service.generate_qrcode_for_payment_in_sats)(request.subject)
    return Response({"qrcode": result.qrcode, "deposit_id": result.deposit_id, "payment_request": result.payment_request}, status.HTTP_200_OK)


@api_view(["POST"])
@authenticated
def generate_qrcode_in_pix(request):
    pass

from uuid import UUID
from typing import Any, cast
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from source.container import affiliate_service
from .serializers import AffiliateRegisterSerializer
from ..authentication.decorators import authenticated
from ..errors import Error, ERROR_CODE_MAPPING
from ..dtos import AffiliateDTO


@api_view(["POST"])
@authenticated
def register_affiliate(request):

    serializer = AffiliateRegisterSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_INPUT.value}, status=status.HTTP_400_BAD_REQUEST)
    affiliate = AffiliateDTO(**cast(dict[str, Any], serializer.validated_data))

    result = affiliate_service.register_new_affiliate(user_id=UUID(request.subject), affiliate=affiliate)
    if result is not None: return Response({"error": result.value}, status=ERROR_CODE_MAPPING.get(result, status.HTTP_400_BAD_REQUEST))

    return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authenticated
def validate_affiliate(request):
    if not affiliate_service.get_affiliate(request.subject):
        return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)
    return Response({"valid": True}, status=status.HTTP_200_OK)

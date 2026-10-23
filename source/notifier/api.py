from typing import Any, cast
from uuid import UUID

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..authentication.decorators import authenticated
from ..container import notifier_service
from ..dtos import NotifierDTO
from ..errors import Error
from .serializers import InputTelegramSerializer


@api_view(["GET", "POST"])
@authenticated
def get_save_notifier(request):

    if request.method == "GET":

        notifier = notifier_service.get_notifier(UUID(request.subject))
        return Response({"telegram_token": notifier.telegram_token, "telegram_id": notifier.telegram_id}, status.HTTP_200_OK)


    if request.method == "POST":

        serializer = InputTelegramSerializer(data=request.data)
        if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)

        validated_data = cast(dict[str, Any], serializer.validated_data)
        notifier = NotifierDTO(**validated_data)

        notifier_service.save_notifier(UUID(request.subject), notifier)

        return Response(status.HTTP_204_NO_CONTENT)

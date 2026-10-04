from typing import cast, Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from ..authentication.decorators import authenticated
from .serializers import ConfigurationSerializer, ExchangeSerializer, AutomationAPISerializer
from ..container import automation_service
from ..errors import Error
from ..dtos import ConfigurationDTO, ApiDTO


@api_view(["GET"])
@authenticated
def automation_dashboard(request):

    exchange = request.query_params.get("exchange", "lnmarkets")
    configuration, credentials, status_automation = automation_service.get_automation_overview(exchange, request.subject)

    return Response({"API_KEY": credentials.API_KEY,
                     "API_SECRET": credentials.API_SECRET,
                     "API_PASSPHRASE": credentials.API_PASSPHRASE,
                     "status_automation": status_automation,
                     "marginUSD": configuration.marginUSD,
                     "leverage": configuration.leverage,
                     "percentage_profit": configuration.percentage_profit,
                     "buy_variation": configuration.buy_variation}, status.HTTP_200_OK)


@api_view(["POST"])
@authenticated
def enable_automation(request):

    serializer = ExchangeSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)    

    exchange = cast(dict[str, str], serializer.validated_data)["exchange"]
    automation_service.enable_automation(exchange, request.subject)

    return Response(status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authenticated
def disable_automation(request):

    serializer = ExchangeSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)    

    exchange = cast(dict[str, str], serializer.validated_data)["exchange"]
    automation_service.disable_automation(exchange, request.subject)

    return Response(status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authenticated
def save_configuration(request):

    serializer = ConfigurationSerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)

    validated_data = cast(dict[str, Any], serializer.validated_data)
    data = ConfigurationDTO(**validated_data)

    automation_service.save_configuration(data.exchange, request.subject, data)
    return Response({"message": "Configuração salva com sucesso."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authenticated
def save_api(request):

    serializer = AutomationAPISerializer(data=request.data)
    if not serializer.is_valid(): return Response({"error": Error.INVALID_CREDENTIALS.value}, status.HTTP_400_BAD_REQUEST)

    validated_data = cast(dict[str, Any], serializer.validated_data)
    data = ApiDTO(**validated_data)

    automation_service.save_api(data.exchange, request.subject, data)
    return Response({"message": "API salva com sucesso."})

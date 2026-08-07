from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..container import dashboard_service
from ..authentication.decorators import authenticated


@api_view(["GET"])
@authenticated
def dashboard(request):

    overview = dashboard_service.overview("lnmarkets", request.subject)

    return Response({"total_profit_today": overview.total_profit_today,
                     "automation": overview.status_automation,
                     "telegram": overview.status_telegram,
                     "payment": overview.status_payment}, status.HTTP_200_OK)

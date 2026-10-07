from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..authentication.decorators import authenticated
from ..telemetry.tracing import tracer
from ..container import operations_service


@api_view(["GET"])
@authenticated
def operations_overview(request):

    with tracer.start_as_current_span("operations_overview"):
        overview = operations_service.get_overview(request.subject)

    return Response({
        "today_operations": overview.today_operations,
        "today_profit": float(overview.today_profit),
        "month_operations": overview.month_operations,
        "month_profit": float(overview.month_profit),
        "all_time_operations": overview.all_time_operations,
        "all_time_profit": float(overview.all_time_profit),
        "total_balance": float(overview.total_balance),
        "total_balance_available": float(overview.total_balance_available),
        "total_balance_exposed": float(overview.total_balance_exposed),
    }, status.HTTP_200_OK)

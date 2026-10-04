from typing import cast

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import GoalSerializer
from ..container import dashboard_service
from ..authentication.decorators import authenticated
from ..telemetry.tracing import tracer


@api_view(["GET"])
@authenticated
def overview(request):

    with tracer.start_as_current_span("overview"):
        overview = dashboard_service.overview("lnmarkets", request.subject)

    return Response({
        "btc_usd_price": overview.btc_usd_price,
        "total_patrimony": overview.total_patrimony,
        "total_margin_exposed": overview.total_margin_exposed,
        "open_orders": overview.open_orders,
        "last_month_profit": overview.last_month_profit,
        "goal_target": overview.goal_target,
        "all_time_profit": overview.all_time_profit,
        "last_operations": overview.last_operations,
        "status_automation": overview.status_automation,
        "status_telegram": overview.status_telegram,
        }, status.HTTP_200_OK)



@api_view(["GET"])
@authenticated
def overview_period(request):

    with tracer.start_as_current_span("overview_period"):
        period = request.query_params.get("period")
        overview_period = dashboard_service.overview_period("lnmarkets", request.subject, period)

    return Response({
        "btc_usd_price": overview_period.btc_usd_price,
        "total_profit": overview_period.total_profit,
        "total_operations": overview_period.total_operations,
        "total_fees": overview_period.total_fees,
        }, status.HTTP_200_OK)



@api_view(["PATCH"])
@authenticated
def update_goal_target(request):

    with tracer.start_as_current_span("dashboard_update_goal"):

        serializer = GoalSerializer(data=request.data)
        if not serializer.is_valid(): return Response({"error": "Goal Sats inválido"}, status.HTTP_400_BAD_REQUEST)

        goal_sats = cast(dict, serializer.validated_data)["goal_target"]
        dashboard_service.update_goal("lnmarkets", request.subject, goal_sats)

        return Response(status=status.HTTP_204_NO_CONTENT)

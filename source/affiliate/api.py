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
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@authenticated
def get_dashboard(request):

    dashboard = affiliate_service.get_affiliate_dashboard_data(UUID(request.subject))

    if isinstance(dashboard, Error):
        return Response({"error": dashboard.value}, status=ERROR_CODE_MAPPING.get(dashboard, status.HTTP_400_BAD_REQUEST))

    return Response({
        "coupon_code": dashboard.coupon_code,
        "tier": dashboard.tier,
        "tier_percentual": dashboard.tier_percentual,
        "total_commissions_brl": float(dashboard.total_commissions_brl),
        "paying_users": dashboard.paying_users,
        "paying_users_threshold": dashboard.paying_users_threshold,
        "next_tier": dashboard.next_tier,
        "next_tier_percentual": dashboard.next_tier_percentual,
        "remaining_to_next": float(dashboard.remaining_to_next),
        "payments": [{
            "date": p.date,
            "coupon": p.coupon,
            "amount_brl": float(p.amount_brl),
            "commission_brl": float(p.commission_brl),
            "status": p.status
        } for p in dashboard.payments]
    })

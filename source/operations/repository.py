import redis
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import cast

from django.db.models import Sum, Count, Q

from .interfaces import OperationsProtocol
from ..constants import CacheKeys
from ..dtos import OperationsResultDTO
from ..dashboard.models import ClosedOrder


class OperationsRepository(OperationsProtocol):

    def __init__(self, cache_client: redis.Redis) -> None:
        self._cache_client = cache_client

    def get_overview(self, user_id: UUID) -> OperationsResultDTO:

        today = datetime.now(timezone.utc).date()
        month_ago = today - timedelta(days=30)

        result = ClosedOrder.objects.filter(user_id=str(user_id)).aggregate(
            today_operations=Count("pk", filter=Q(closed_at__date=today)),
            today_profit=Sum("profit", filter=Q(closed_at__date=today)),
            month_operations=Count("pk", filter=Q(closed_at__date__gte=month_ago)),
            month_profit=Sum("profit", filter=Q(closed_at__date__gte=month_ago)),
            all_time_operations=Count("pk"),
            all_time_profit=Sum("profit"),
        )

        balance = cast(dict[str, str], self._cache_client.hgetall(f"{CacheKeys.USER_BALANCE}:{user_id}"))

        return OperationsResultDTO(
            today_operations=result["today_operations"] or 0,
            today_profit=result["today_profit"] or Decimal("0"),
            month_operations=result["month_operations"] or 0,
            month_profit=result["month_profit"] or Decimal("0"),
            all_time_operations=result["all_time_operations"] or 0,
            all_time_profit=result["all_time_profit"] or Decimal("0"),
            total_balance=Decimal(balance.get("total_balance", "0")),
            total_balance_available=Decimal(balance.get("total_balance_available", "0")),
            total_balance_exposed=Decimal(balance.get("total_balance_exposed", "0")),
        )

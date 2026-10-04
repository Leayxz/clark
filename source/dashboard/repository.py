import redis, json
from typing import Any, cast
from uuid import UUID
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal

from .models import ClosedOrder
from .interfaces import DashboardProtocol
from ..constants import CacheKeys
from ..dtos import Overview, OverviewPeriod
from ..constants import Period
from ..telemetry.tracing import tracer


class DashboardRepository(DashboardProtocol):

    def __init__(self, client: redis.Redis) -> None:
        self._cache_client = client


    def get_overview(self, exchange: str, user_id: UUID) -> Overview:

        with self._cache_client.pipeline() as pipe:
            payload = {"exchange": exchange, "user_id": user_id}
            pipe.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
            pipe.hgetall(f"{CacheKeys.RISK_EXPOSURE}:{user_id}")
            pipe.get(f"{CacheKeys.GOAL_TARGET}:{user_id}")
            pipe.hget(f"{CacheKeys.TOTAL_PATRIMONY}:{user_id}", "total_patrimony")
            pipe.hget(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_OPEN_ORDERS_COUNT)
            pipe.get(f"BTC_USD_PRICE")

            automation, total_margin_used, goal_target, total_patrimony, open_orders, btc_usd_price = cast(tuple[int, dict[str, int], int, int, int, int], pipe.execute())

        thirty_days_ago = timezone.now() - timedelta(days=30)
        last_operations = list(ClosedOrder.objects.filter(user_id=user_id).order_by("-closed_at")[:4])
        result = (ClosedOrder.objects.filter(user_id=user_id).aggregate(operations=Count("user_id"),
                                                                        last_month_profit=Sum("profit", filter=Q(closed_at__gte=thirty_days_ago)),
                                                                        profit=Sum("profit"),
                                                                        fees=Sum("total_fees")
                                                                        ))

        return Overview(
            btc_usd_price=btc_usd_price,
            total_patrimony=total_patrimony,
            total_margin_exposed=total_margin_used.get("total_margin_used") or 0,
            open_orders=open_orders,
            all_time_profit=result.get("profit") or 0,
            last_month_profit=result.get("last_month_profit") or 0,
            status_automation=True if automation else False,
            status_telegram=False,
            goal_target=goal_target,
            last_operations=[{"tipo": "Venda", "profit": operation.profit, "closed_at": operation.closed_at, "closed_at": operation.closed_at.strftime("%H:%M") if operation.closed_at else None} for operation in last_operations],
        )


    def get_overview_period(self, exchange: str, user_id: UUID, period: Period) -> OverviewPeriod:
        with tracer.start_as_current_span("repository.get_dashboard_data"):

            btc_usd_price = self._cache_client.get(f"BTC_USD_PRICE") or 0

            filters: dict[str, Any] = {"user_id": user_id}

            if period == Period.TODAY:
                filters["closed_at__gte"] = timezone.localtime().replace(hour=0, minute=0, second=0,microsecond=0)

            elif period == Period.MONTH:
                filters["closed_at__gte"] = timezone.now() - timedelta(days=30)

            result = ClosedOrder.objects.filter(**filters).aggregate(operations=Count("user_id"), profit=Sum("profit"), fees=Sum("total_fees"))

            return OverviewPeriod(
                btc_usd_price=Decimal(f"{btc_usd_price}"),                
                total_profit=result.get("profit") or 0,
                total_operations=result.get("operations") or 0,
                total_fees=result.get("fees") or 0,
            )


    def update_goal_target(self, exchange: str, user_id: UUID, goal_target: int) -> None:
        self._cache_client.set(f"{CacheKeys.GOAL_TARGET}:{user_id}", str(goal_target), CacheKeys.THIRTY_DAYS_IN_SECONDS)

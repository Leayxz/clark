import redis, json
from typing import Any, cast
from uuid import UUID
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.db.models import Sum, Count, Q

from .models import ClosedOrder
from .interfaces import DashboardProtocol
from ..constants import CacheKeys
from ..dtos import Overview, OverviewPeriod, SidebarStatus
from ..constants import Period
from ..telemetry.tracing import tracer


class DashboardRepository(DashboardProtocol):

    def __init__(self, client: redis.Redis) -> None:
        self._cache_client = client


    def get_overview(self, exchange: str, user_id: UUID) -> Overview:

        with self._cache_client.pipeline() as pipe:
            payload = {"exchange": exchange, "user_id": user_id}
            pipe.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
            pipe.hgetall(f"{CacheKeys.USER_BALANCE}:{user_id}")
            pipe.get(f"{CacheKeys.GOAL_TARGET}:{user_id}")
            pipe.hget(f"{CacheKeys.DASHBOARD_ACCOUNT_OVERVIEW}:{user_id}", CacheKeys.DASHBOARD_OPEN_ORDERS_COUNT)
            pipe.get(f"BTC_USD_PRICE")

            automation, user_balance, goal_target, open_orders, btc_usd_price = cast(tuple[int, dict[str, str], str | None, str | None, str | None], pipe.execute())

        thirty_days_ago = timezone.now() - timedelta(days=30)
        last_operations = list(ClosedOrder.objects.filter(user_id=user_id).order_by("-closed_at")[:4])
        result = (ClosedOrder.objects.filter(user_id=user_id).aggregate(operations=Count("user_id"),
                                                                        last_month_profit=Sum("profit", filter=Q(closed_at__gte=thirty_days_ago)),
                                                                        profit=Sum("profit"),
                                                                        fees=Sum("total_fees")
                                                                        ))

        return Overview(
            btc_usd_price=int(btc_usd_price) if btc_usd_price else 0,
            total_patrimony=int(user_balance.get("total_balance", "0")),
            total_margin_exposed=int(user_balance.get("total_balance_exposed", "0")),
            open_orders=int(open_orders) if open_orders else 0,
            all_time_profit=result.get("profit") or 0,
            last_month_profit=result.get("last_month_profit") or 0,
            goal_target=int(goal_target) if goal_target else 0,
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


    def get_sidebar_data(self, exchange: str, user_id: UUID) -> SidebarStatus:

        with tracer.start_as_current_span("repository.get_sidebar_data"):

            with self._cache_client.pipeline() as pipe:
                payload = {"exchange": exchange, "user_id": user_id}
                pipe.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
                pipe.get(f"{CacheKeys.NOTIFIER_TELEGRAM}:{user_id}")
                pipe.hgetall(f"{CacheKeys.AUTOMATION_CONFIGURATION}:{exchange}:{user_id}")

                automation, notifier_raw, configuration = cast(tuple[int, bytes | None, dict[str, str]], pipe.execute())

            notifier: dict[str, str] = json.loads(notifier_raw) if notifier_raw else {}

            last_operation = (ClosedOrder.objects.filter(user_id=user_id)
                              .order_by("-closed_at")
                              .values_list("closed_at", flat=True)
                              .first())

            return SidebarStatus(
                last_operation=last_operation.strftime("%H:%M") if last_operation else "",
                status_automation=True if automation else False,
                status_telegram=bool(notifier.get("telegram_id")),
                leverage=int(configuration.get("leverage") or 0),
                percentage_profit=Decimal(configuration.get("percentage_profit") or 0),
            )


    def update_goal_target(self, exchange: str, user_id: UUID, goal_target: int) -> None:
        self._cache_client.set(f"{CacheKeys.GOAL_TARGET}:{user_id}", str(goal_target), CacheKeys.THIRTY_DAYS_IN_SECONDS)

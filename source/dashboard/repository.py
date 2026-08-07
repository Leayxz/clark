import redis, json
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

from .models import ClosedOrder
from .interfaces import DashboardProtocol
from ..constants import CacheKeys


class DashboardRepository(DashboardProtocol):

    def __init__(self, client: redis.Redis) -> None:
        self._client = client


    def get_status_automation(self, exchange: str, email: str) -> bool:
        """
        - Busca todas as automações rodando no cache, que é um set, diretamente em O(1).
        - Caso exista, retorna True, caso não, False, o próprio método `sismember()` retorna 0 ou 1.
        """
        payload = {"exchange": exchange, "email": email}
        automation = self._client.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
        return True if automation else False


    def get_total_profit_today(self,) -> Decimal | None:
        today = timezone.localdate()
        result = ClosedOrder.objects.filter(closed_at__date=today).aggregate(sum_profit=Sum("profit"))
        return Decimal(f"{result['sum_profit']}") if result['sum_profit'] else None

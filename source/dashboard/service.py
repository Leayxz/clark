from .interfaces import DashboardProtocol
from ..dtos import DashboardResult


class DashboardService:

    def __init__(self, repository: DashboardProtocol) -> None:
        self._repository = repository


    def overview(self, exchange: str, email: str) -> DashboardResult:
        status_automation = self._repository.get_status_automation(exchange, email)
        total_profit_today = self._repository.get_total_profit_today()

        return DashboardResult(total_profit_today=total_profit_today,
                               status_automation=status_automation,
                               status_telegram=False,
                               status_payment=False)

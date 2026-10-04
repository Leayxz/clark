from .interfaces import DashboardProtocol
from ..dtos import Overview, OverviewPeriod, SidebarStatus
from ..constants import Period


class DashboardService:

    def __init__(self, repository: DashboardProtocol) -> None:
        self._repository = repository


    def overview(self, exchange: str, user_id: str) -> Overview:
        return self._repository.get_overview(exchange, user_id)


    def overview_period(self, exchange: str, user_id: str, period: str) -> OverviewPeriod:
        return self._repository.get_overview_period(exchange, user_id, period)


    def get_sidebar_data(self, exchange: str, user_id: str) -> SidebarStatus:
        return self._repository.get_sidebar_data(exchange, user_id)


    def update_goal(self, exchange: str, user_id: str, goal_target: int) -> None:
        self._repository.update_goal_target(exchange, user_id, goal_target)

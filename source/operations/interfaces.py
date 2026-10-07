from uuid import UUID
from ..dtos import OperationsResultDTO


class OperationsProtocol:
    def get_overview(self, user_id: UUID) -> OperationsResultDTO: ...

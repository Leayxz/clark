from uuid import UUID
from .interfaces import OperationsProtocol
from ..dtos import OperationsResultDTO


class OperationsService:

    def __init__(self, repository: OperationsProtocol):
        self._repository = repository

    def get_overview(self, user_id: UUID) -> OperationsResultDTO:
        return self._repository.get_overview(user_id)

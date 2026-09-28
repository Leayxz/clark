from uuid import UUID
from .interfaces import AffiliateProtocol
from ..errors import Error
from ..dtos import AffiliateDTO


class AffiliateService:

    def __init__(self, repository: AffiliateProtocol):
        self._repository = repository

    def get_affiliate(self, user_id: UUID) -> bool:
        return self._repository.get_affiliate(user_id)

    def register_new_affiliate(self, user_id: UUID, affiliate: AffiliateDTO) -> Error | None:
        return self._repository.register_new_affiliate(user_id, affiliate)

from typing import Protocol
from uuid import UUID

from ..dtos import AffiliateDTO
from ..errors import Error


class AffiliateProtocol(Protocol):
    def get_affiliate(self, user_id: UUID) -> bool: ...
    def register_new_affiliate(self, user_id: UUID, affiliate: AffiliateDTO) -> Error | None: ...

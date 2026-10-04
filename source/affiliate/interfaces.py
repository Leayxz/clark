from typing import Protocol
from uuid import UUID
from decimal import Decimal

from ..dtos import AffiliateDTO, AffiliateDashboardDTO
from ..errors import Error
from .models import Affiliate


class AffiliateProtocol(Protocol):
    def get_affiliate(self, user_id: UUID) -> bool: ...
    def get_affiliate_by_user(self, user_id: UUID) -> Affiliate | None: ...
    def register_new_affiliate(self, user_id: UUID, affiliate: AffiliateDTO) -> Error | None: ...
    def get_affiliate_dashboard_data(self, coupon_code: str) -> AffiliateDashboardDTO: ...

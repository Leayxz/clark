from uuid import UUID
from .interfaces import AffiliateProtocol
from ..errors import Error
from ..dtos import AffiliateDTO, AffiliateDashboardDTO
from .models import Affiliate


class AffiliateService:

    def __init__(self, repository: AffiliateProtocol):
        self._repository = repository


    def get_affiliate(self, user_id: UUID) -> bool:
        return self._repository.get_affiliate(user_id)


    def register_new_affiliate(self, user_id: UUID, affiliate: AffiliateDTO) -> Error | None:
        return self._repository.register_new_affiliate(user_id, affiliate)


    def get_affiliate_dashboard_data(self, user_id: UUID) -> AffiliateDashboardDTO | Error:
        affiliate = self._validate_affiliate(user_id)
        if isinstance(affiliate, Error): return affiliate
        return self._repository.get_affiliate_dashboard_data(affiliate.coupon_code)


    def _validate_affiliate(self, user_id: UUID) -> Affiliate | Error:
        affiliate = self._repository.get_affiliate_by_user(user_id)
        if not affiliate: return Error.AFFILIATE_NOT_FOUND
        return affiliate

from uuid import UUID

from django.db import IntegrityError

from .models import Affiliate
from ..errors import Error
from ..dtos import AffiliateDTO
from ..telemetry.tracing import tracer
from ..telemetry.logging import logger


class AffiliateRepository:

    def get_affiliate(self, user_id: UUID) -> bool:

        with tracer.start_as_current_span("repository.get_affiliate"):
            return Affiliate.objects.filter(user_id=user_id).exists()

    def register_new_affiliate(self, user_id: UUID, affiliate: AffiliateDTO) -> Error | None:

        with tracer.start_as_current_span("repository.register_new_affiliate"):

            try:
                Affiliate.objects.create(user_id=user_id, coupon_code=affiliate.coupon, liquid_address=affiliate.liquid_address, promotion_description=affiliate.promotion_description)
                logger.info("💾 Afiliado registrado com sucesso", extra={"user_id": str(user_id), "coupon": affiliate.coupon})

            except IntegrityError as error:
                logger.error("❌ Falha ao registrar afiliado", extra={"user_id": str(user_id), "error": str(error)}, exc_info=True)

                if "user_id" in str(error):
                    return Error.AFFILIATE_ALREADY_EXISTS

                if "coupon_code" in str(error):
                    return Error.COUPON_ALREADY_EXISTS

                if "liquid_address" in str(error):
                    return Error.LIQUID_ADDRESS_EXISTS

                return Error.PROVIDER_ERROR

            return None

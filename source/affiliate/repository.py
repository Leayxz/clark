from decimal import Decimal
from uuid import UUID

from django.db import IntegrityError
from django.db.models import Count, Q, Sum

from ..constants import AffiliateCommission, AffiliateTier, PaymentStatus
from ..dtos import AffiliateDashboardDTO, AffiliateDTO, AffiliatePayment
from ..errors import Error
from ..payment.models import Invoice
from ..telemetry.logging import logger
from ..telemetry.tracing import tracer
from .models import Affiliate


class AffiliateRepository:

    def get_affiliate(self, user_id: UUID) -> bool:
        with tracer.start_as_current_span("repository.get_affiliate"):
            return Affiliate.objects.filter(user_id=user_id).exists()


    def get_affiliate_by_user(self, user_id: UUID) -> Affiliate | None:
        with tracer.start_as_current_span("repository.get_affiliate_by_user"):
            return Affiliate.objects.filter(user_id=user_id).first()


    def get_affiliate_dashboard_data(self, coupon_code: str) -> AffiliateDashboardDTO:
        with tracer.start_as_current_span("repository.get_affiliate_dashboard_data"):

            aggregate = Invoice.objects.filter(coupon_code=coupon_code).aggregate(
                paying_users=Count("id", filter=Q(payment_status__in=[PaymentStatus.PAID, PaymentStatus.PROCESSED])),
                total_commissions=Sum("affiliate_commission_amount", filter=Q(payment_status=PaymentStatus.PROCESSED))
            )

            invoices = Invoice.objects.filter(coupon_code=coupon_code).order_by("-created_at")[:10]

            paying_users = aggregate["paying_users"] or 0
            total_commissions = aggregate["total_commissions"] or Decimal("0")

            payments = [
                AffiliatePayment(
                    date=invoice.created_at.strftime("%d %b %Y"),
                    coupon=invoice.coupon_code or "",
                    amount_brl=invoice.amount_brl,
                    commission_brl=Decimal(invoice.affiliate_commission_amount or 0),
                    status=invoice.payment_status,
                )
                for invoice in invoices
            ]

            if paying_users >= AffiliateTier.OURO:
                tier, tier_percentual = "Ouro", AffiliateCommission.OURO
                next_tier, next_threshold, next_percentual = "—", 0, 0
                remaining = Decimal("0")

            elif paying_users >= AffiliateTier.PRATA:
                tier, tier_percentual = "Prata", AffiliateCommission.PRATA
                next_tier, next_threshold, next_percentual = "Ouro", AffiliateTier.OURO, AffiliateCommission.OURO
                remaining = Decimal(AffiliateTier.OURO - paying_users)

            else:
                tier, tier_percentual = "Bronze", AffiliateCommission.BRONZE
                next_tier, next_threshold, next_percentual = "Prata", AffiliateTier.PRATA, AffiliateCommission.PRATA
                remaining = Decimal(AffiliateTier.PRATA - paying_users)

            return AffiliateDashboardDTO(
                coupon_code=coupon_code,
                tier=tier,
                tier_percentual=tier_percentual,
                total_commissions_brl=total_commissions,
                paying_users=paying_users,
                paying_users_threshold=next_threshold - paying_users,
                next_tier=next_tier,
                next_tier_percentual=next_percentual,
                remaining_to_next=remaining,
                payments=payments,
            )


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

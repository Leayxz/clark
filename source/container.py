import redis

from .authentication.service import AuthService
from .authentication.repository import AuthenticationRepository

from .payment.repository import PaymentRepository
from .payment.providers.deflowexchange import DeflowExchangeProvider
from .payment.gateway import ExchangeGateway
from .payment.service import PaymentService

from .automation.service import AutomationService
from .automation.repository import AutomationRepository

from .notifier.service import NotifierService
from .notifier.repository import NotifierRepository

from .dashboard.service import DashboardService
from .dashboard.repository import DashboardRepository

from .affiliate.repository import AffiliateRepository
from .affiliate.service import AffiliateService


redis_client = redis.Redis(decode_responses=True)

automation_repository = AutomationRepository(redis_client)
automation_service = AutomationService(automation_repository)

authentication_database = AuthenticationRepository()
authentication_service = AuthService(authentication_database)

deflow_provider = DeflowExchangeProvider()
payment_gateway = ExchangeGateway(provider=deflow_provider)
payment_repository = PaymentRepository(redis_client)

affiliate_repository = AffiliateRepository()
affiliate_service = AffiliateService(affiliate_repository)

payment_service = PaymentService(payment_repository, payment_gateway)

dashboard_repository = DashboardRepository(redis_client)
notifier_repository = NotifierRepository(redis_client)
dashboard_service = DashboardService(dashboard_repository)

notifier_service = NotifierService(notifier_repository)

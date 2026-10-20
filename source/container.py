import redis

from .affiliate.repository import AffiliateRepository
from .affiliate.service import AffiliateService
from .authentication.repository import AuthenticationRepository
from .authentication.service import AuthService
from .automation.repository import AutomationRepository
from .automation.service import AutomationService
from .dashboard.repository import DashboardRepository
from .dashboard.service import DashboardService
from .notifier.repository import NotifierRepository
from .notifier.service import NotifierService
from .operations.repository import OperationsRepository
from .operations.service import OperationsService
from .payment.gateway import ExchangeGateway
from .payment.providers.deflowexchange import DeflowExchangeProvider
from .payment.repository import PaymentRepository
from .payment.service import PaymentService

redis_client = redis.Redis(decode_responses=True, socket_connect_timeout=2, socket_timeout=2)

automation_repository = AutomationRepository(redis_client)
automation_service = AutomationService(automation_repository)

authentication_database = AuthenticationRepository()
authentication_service = AuthService(authentication_database)

deflow_provider = DeflowExchangeProvider()
payment_gateway = ExchangeGateway(provider=deflow_provider)
payment_repository = PaymentRepository(redis_client)
payment_service = PaymentService(payment_repository, payment_gateway)

affiliate_repository = AffiliateRepository()
affiliate_service = AffiliateService(affiliate_repository)

operations_repository = OperationsRepository(redis_client)
operations_service = OperationsService(operations_repository)

dashboard_repository = DashboardRepository(redis_client)
dashboard_service = DashboardService(dashboard_repository)

notifier_repository = NotifierRepository(redis_client)
notifier_service = NotifierService(notifier_repository)

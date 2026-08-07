import redis

from .authentication.service import AuthService
from .authentication.repository import AuthenticationRepository

from .payment.repository import PaymentRepository
from .payment.providers.lnmarkets import LNMarketsPaymentProvider
from .payment.service import PaymentService

from .automation.service import AutomationService
from .automation.repository import AutomationRepository

from .notifier.service import NotifierService
from .notifier.repository import NotifierRepository

from .dashboard.service import DashboardService
from .dashboard.repository import DashboardRepository


redis_client = redis.Redis() 

automation_repository = AutomationRepository(redis_client)
automation_service = AutomationService(automation_repository)

authentication_database = AuthenticationRepository()
authentication_service = AuthService(authentication_database)

payment_repository = PaymentRepository()
payment_provider = LNMarketsPaymentProvider()
payment_service = PaymentService(payment_repository, payment_provider)

dashboard_repository = DashboardRepository(redis_client)
dashboard_service = DashboardService(dashboard_repository)

notifier_repository = NotifierRepository(redis_client)
notifier_service = NotifierService(notifier_repository)

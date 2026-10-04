from enum import Enum
from decimal import Decimal


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSED = "PROCESSED"
    REFUNDED = "REFUNDED"


class AffiliateTier:
    BRONZE = 5
    PRATA = 10
    OURO = 20


class EXCHANGES:
    LNMARKETS = "lnmarkets"
    HYPERLIQUID = "hyperliquid"


class CacheKeys:
    ALL_ACTIVATED_AUTOMATION = "all_activated_automation"
    AUTOMATION_CONFIGURATION = "automation_configuration"
    AUTOMATION_API = "automation_api"
    AUTOMATION_CREDENTIALS = "automation_credentials"
    THIRTY_DAYS_IN_SECONDS = 60*60*24*30
    DASHBOARD_ACCOUNT_OVERVIEW = "dashboard_account_overview"
    DASHBOARD_TOTAL_MARGIN_USED = "total_margin_used"
    DASHBOARD_OPEN_ORDERS_COUNT = "open_orders_count"
    TOTAL_PATRIMONY = "total_patrimony"
    RISK_EXPOSURE = "risk_exposure"
    GOAL_TARGET = "goal_target"
    NOTIFIER_TELEGRAM = "notifier_telegram"


class Period:
    TODAY = "today"
    MONTH = "month"
    ALL_TIME = "all_time"


class Automation:
    PRICE_IN_BRL = Decimal("150")

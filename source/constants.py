from decimal import Decimal
from enum import Enum


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
    # separar CacheKeys e CacheValues
    ALL_ACTIVATED_AUTOMATION = "all_activated_automation"
    AUTOMATION_CONFIGURATION = "automation_configuration"
    AUTOMATION_CREDENTIALS = "automation_credentials"
    THIRTY_DAYS_IN_SECONDS = 60*60*24*30
    DASHBOARD_ACCOUNT_OVERVIEW = "dashboard_account_overview"
    DASHBOARD_OPEN_ORDERS_COUNT = "open_orders_count"
    USER_BALANCE = "user_balance"
    BALANCE_TOTAL = "total_balance"
    BALANCE_AVAILABLE = "total_balance_available"
    BALANCE_EXPOSED = "total_balance_exposed"
    GOAL_TARGET = "goal_target"
    NOTIFIER_TELEGRAM = "notifier_telegram"


class Period:
    TODAY = "today"
    MONTH = "month"
    ALL_TIME = "all_time"


class Automation:
    PRICE_IN_BRL = Decimal("150")

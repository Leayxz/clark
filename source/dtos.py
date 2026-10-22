from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .errors import Error


@dataclass
class AuthDTO:
    email: str
    password: str


@dataclass
class AffiliateDTO:
    liquid_address: str
    coupon: str
    promotion_description: str


@dataclass
class AffiliatePayment:
    date: str
    coupon: str
    amount_brl: Decimal
    commission_brl: Decimal
    status: str


@dataclass
class AffiliateDashboardDTO:
    coupon_code: str
    tier: str
    tier_percentual: int
    total_commissions_brl: Decimal
    paying_users: int
    paying_users_threshold: int
    next_tier: str
    next_tier_percentual: int
    remaining_to_next: Decimal
    payments: list[AffiliatePayment]


@dataclass
class AuthResult:
    subject: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    new_access_token: str | None = None
    new_refresh_token: str | None = None
    error: Error | None = None


@dataclass
class DeflowExchangeDTO:
    payment_id: str
    qr_code: str
    amount_brl: Decimal
    status: str
    expires_at: datetime | None = None
    coupon: str = ""
    affiliate_commission_rate: int = 0
    affiliate_commission_amount: Decimal = Decimal("0")


@dataclass
class LNMarketsDTO:
    deposit_id: str
    payment_request: str


@dataclass
class PaymentDTO:
    coupon_code: str
    payer_tax_number: str


@dataclass
class NotifierDTO:
    telegram_id: str | None = None
    telegram_token: str | None = None


@dataclass
class SidebarStatus:
    last_operation: str
    status_automation: bool
    status_telegram: bool
    leverage: int
    percentage_profit: Decimal | int


@dataclass
class Overview:
    btc_usd_price: Decimal
    total_patrimony: int
    total_margin_exposed: int
    open_orders: int
    goal_target: int
    all_time_profit: Decimal | int
    last_month_profit: Decimal | int
    last_operations: list[dict]


@dataclass
class OverviewPeriod:
    btc_usd_price: Decimal
    total_profit: Decimal | int
    total_operations: int
    total_fees: Decimal | int



@dataclass
class ApiDTO:
    API_KEY: str | None = None
    API_SECRET: str | None = None
    API_PASSPHRASE: str | None = None
    exchange: str | None = None


@dataclass
class CredentialsDTO:
    API_KEY: str
    API_SECRET: str
    API_PASSPHRASE: str
    EXCHANGE: str


@dataclass
class ConfigurationDTO:
    """
    - marginUSD: int
    - leverage: int
    - percentage_profit: Decimal
    - buy_variation: Decimal
    - last_buy_up: Decimal
    - last_buy_down: Decimal
    """
    marginUSD: int = 0
    leverage: int = 0
    percentage_profit: Decimal = Decimal("0.000")
    buy_variation: Decimal = Decimal("0")
    last_buy_up: Decimal = Decimal("0")
    last_buy_down: Decimal = Decimal("0")
    exchange: str = ""


@dataclass
class AutomationDTO:
    """
    Visao completa da automacao do usuario em uma exchange, lida em uma unica
    ida ao cache (pipeline): configuracao + credenciais + status de ativacao.

    - marginUSD: int
    - leverage: int
    - percentage_profit: Decimal
    - buy_variation: Decimal
    - last_buy_up: Decimal
    - last_buy_down: Decimal
    - exchange: str
    - API_KEY / API_SECRET / API_PASSPHRASE: str | None
    - status_automation: bool
    """
    marginUSD: int = 0
    leverage: int = 0
    percentage_profit: Decimal = Decimal("0.000")
    buy_variation: Decimal = Decimal("0")
    last_buy_up: Decimal = Decimal("0")
    last_buy_down: Decimal = Decimal("0")
    exchange: str = ""
    API_KEY: str | None = None
    API_SECRET: str | None = None
    API_PASSPHRASE: str | None = None
    status_automation: bool = False


@dataclass
class AllOpenOrdersDTO:
    """
    - order_id: str
    - entry_price: Decimal
    """
    order_id: str
    entry_price: Decimal


@dataclass
class BuyOrderDTO:
    """
    - order_id: str
    - entry_price: Decimal
    - margin_used: Decimal
    """
    order_id: str
    entry_price: Decimal
    margin_used: Decimal


@dataclass
class SellOrderDTO:
    """
    - order_id: str
    - profit: Decimal
    - sum_funding_fees: Decimal
    """
    order_id: str
    exit_price: Decimal
    margin_used: Decimal
    profit: Decimal
    total_fees: Decimal
    closed_at: datetime


@dataclass
class OperationsResultDTO:
    today_operations: int
    today_profit: Decimal
    month_operations: int
    month_profit: Decimal
    all_time_operations: int
    all_time_profit: Decimal
    total_balance: Decimal
    total_balance_available: Decimal
    total_balance_exposed: Decimal

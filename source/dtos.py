from dataclasses import dataclass
from decimal import Decimal
from .errors import Error

@dataclass
class AuthDTO:
    email: str
    password: str


@dataclass
class AuthResult:
    subject: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    new_access_token: str | None = None
    new_refresh_token: str | None = None
    error: Error | None = None


@dataclass
class LNMarketsDTO:
    deposit_id: str
    payment_request: str


@dataclass
class PaymentDTO:
    deposit_id: str
    payment_request: str
    qrcode: str


@dataclass
class NotifierDTO:
    telegram_id: str | None = None
    telegram_token: str | None = None


@dataclass
class DashboardResult:
    total_profit_today: Decimal | None
    status_automation: bool
    status_telegram: bool
    status_payment: bool


@dataclass
class ApiDTO:
    API_KEY: str | None = None
    API_SECRET: str | None = None
    API_PASSPHRASE: str | None = None
    exchange: str | None = None


@dataclass
class ConfigurationDTO:
    """
    - wallet_balance: Decimal
    - marginUSD: int
    - leverage: int
    - percentage_profit: Decimal
    - buy_variation: Decimal
    - last_buy_up: Decimal
    - last_buy_down: Decimal
    """
    wallet_balance: Decimal = Decimal("0")
    marginUSD: int = 1
    leverage: int = 5
    percentage_profit: Decimal = Decimal("0.005")
    buy_variation: Decimal = Decimal("500")
    last_buy_up: Decimal = Decimal("0")
    last_buy_down: Decimal = Decimal("0")


@dataclass
class AllOpenOrders:
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


@dataclass
class CredentialsDTO:
    """
    - API_KEY: str
    - API_SECRET: str
    - API_PASSPHRASE: str
    """
    API_KEY: str
    API_SECRET: str
    API_PASSPHRASE: str
    exchange: str

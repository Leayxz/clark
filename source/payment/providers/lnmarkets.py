from lnmarkets_sdk.rest.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.rest.v3.models.account import DepositLightningParams

from ..interfaces import ProviderProtocol
from ...dtos import LNMarketsDTO
from ...configurations import APILNMarkets

class LNMarketsPaymentProvider(ProviderProtocol):

    async def create_deposit_in_sats(self, email: str, automation_price: int) -> LNMarketsDTO:
        authentication = APIAuthContext(key=APILNMarkets.API_KEY, secret=APILNMarkets.API_SECRET, passphrase=APILNMarkets.API_PASSPHRASE)
        config = APIClientConfig(authentication=authentication, network="mainnet")

        async with LNMClient(config) as client:
            intention = DepositLightningParams(amount=automation_price, comment=f"Payment for {email}")
            invoice = await client.account.deposit_lightning(intention)
            return LNMarketsDTO(deposit_id=invoice.deposit_id, payment_request=invoice.payment_request)

import json
from dataclasses import dataclass
from asgiref.sync import sync_to_async


options = {"key": config("LNM_API_KEY"), "secret": config("LNM_SECRET_KEY"), "passphrase": config("LNM_PASSPHRASE"), "network": 'mainnet'}
lnm = rest.LNMarketsRest(**options)


@dataclass
class LNMarketResult:
      sucesso: bool
      deposit_id: str | None = None
      payment_request: str | None = None

class LNMarket:

      def __init__(self, log_sys) -> None:
            self._log_sys = log_sys

      async def gerar_novo_deposito(self, preco_em_sats: float):

            resposta = await sync_to_async(lnm.new_deposit)({"amount": preco_em_sats})
            
            if "message" in resposta:
                  self._log_sys().error(f"❌ Resposta Inválida invoice LnMarkets: {resposta}")
                  return LNMarketResult(sucesso=False)

            dados = json.loads(resposta)
            return LNMarketResult(sucesso=True, deposit_id=dados["depositId"], payment_request=dados["paymentRequest"])

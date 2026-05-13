import base64, qrcode
from dataclasses import dataclass
from io import BytesIO
from time import time

@dataclass
class PagamentoResult:
      sucesso: bool
      status_code: int
      mensagem: str | None = None
      qrcode: str | None = None
      id_invoice: str | None = None
      payment_hash: str | None = None

class Pagamento:

      def __init__(self, cache, log_user, provider_pagamento) -> None:
            self._cache = cache
            self._log_user = log_user
            self._provider_pagamento = provider_pagamento

      async def gerar_invoice(self, username):

            # 1. Valor atual do BTC e transformação para SATS
            preco_atual_btc = self._cache.get("preco_atual") # Vem do cache, talvez mudar?
            preco_em_sats = self._transformar_preco_em_sats(preco_atual_btc)

            # 2. Abre invoice pendente - Intenção de fazer pagamento
            deposito = await self._provider_pagamento.novo_deposito(preco_em_sats=preco_em_sats) # Tenho log aqui dentro? Se não, preciso logar aqui em baixo
            if not deposito.sucesso: return PagamentoResult(sucesso=False, status_code=deposito.status_code, mensagem=deposito.mensagem)

            # 3. Armazena email + id invoice NÃO PAGO em cache por 30 dias
            invoice = {'username': username, 'id_invoice': deposito.deposit_id, 'timestamp': time() * 1000, 'status': False}
            self._cache.set(f"INVOICE_{username}", invoice)

            # 4. Gera qrcode base64 - Deveria ser async?
            buffer = BytesIO()
            qrc = qrcode.make(deposito.payment_request)
            qrc.save(buffer, "PNG")
            qrc_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            self._log_user(username=username).info(f"QRCode Gerado.")
            return PagamentoResult(sucesso=True, status_code=200, qrcode=qrc_base64, id_invoice=deposito.deposit_id, payment_hash=deposito.payment_request)


      def _transformar_preco_em_sats(self, preco_atual_btc):
            ticket_automacao = 1 # Real
            return int((ticket_automacao / preco_atual_btc) * 100_000_000) # Converte o valor do ticket para sats, considerando o preço atual do BTC

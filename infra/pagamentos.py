import json, qrcode, base64, time, httpx
from io import BytesIO
from lnmarkets import rest
from decouple import config
from django.core.cache import cache
from infra.models import InvoicesPagos
from infra.index import log_sys, log_user
from dataclasses import dataclass
from asgiref.sync import sync_to_async

options = {"key": config("LNM_API_KEY"), "secret": config("LNM_SECRET_KEY"), "passphrase": config("LNM_PASSPHRASE"), "network": 'mainnet'}
lnm = rest.LNMarketsRest(**options)

@dataclass
class PagamentoResult:
      sucesso: bool
      qrcode: str | None = None
      id_invoice: str | None = None
      payment_hash: str | None = None

class Pagamento:

      def __init__(self, user) -> None:
            self._user = user

      async def gerar_invoice(self) -> PagamentoResult:

            # 1. Valor atual do btc e transformação para sats
            preco_atual_btc = await httpx.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCBRL").json()["price"] # debt: Abstrair Infra
            preco_em_sats = self._transformar_preco_em_sats(preco_atual_btc)

            # 2. Abre invoice pendente na LNMarkets - Intenção de compra
            resposta = await sync_to_async(lnm.new_deposit)({"amount": preco_em_sats})
            if 'message' in resposta: log_sys().error(f"❌ Resposta Inválida Invoice LnMarkets: {resposta}"); return PagamentoResult(sucesso=False)
            intencao_compra = json.loads(resposta)

            # 3. Armazena email + id invoice em cache por 30 dias
            invoice = {'username': self._user.username, 'id_invoice': intencao_compra['depositId'], 'timestamp': time.time() * 1000, 'status': False}
            cache.set(f"INVOICE_{self._user.username}", invoice)

            # 4. Gera qrcode base64 - Deveria ser async?
            qrc = qrcode.make(intencao_compra["paymentRequest"])
            buffer = BytesIO()
            qrc.save(buffer, "PNG")
            qrc_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            log_user(username=self._user.username).info(f"QRCode Gerado.")
            return PagamentoResult(sucesso=True, qrcode=qrc_base64, id_invoice=intencao_compra['depositId'], payment_hash=intencao_compra["paymentRequest"])


      async def validar_invoice(self) -> PagamentoResult:

            # BUSCA INVOICE EM CACHE E SE NAO EXISTIR TENTA NO DB
            ultimo_invoice = cache.get(f"INVOICE_{self._user.username}")
            if ultimo_invoice == None:
                  try: # debt: SUBSTITUIR ISSO POR MIDDLEWARE GLOBAL DE EXCEPTIONS
                        ultimo_invoice = await sync_to_async(InvoicesPagos.objects.filter(user=self._user).latest)('timestamp')
                        invoice_cache = { 'username': self._user.username, 'id_invoice': ultimo_invoice.id_invoice, 'timestamp': ultimo_invoice.timestamp, 'status': ultimo_invoice.status }
                        cache.set(f"INVOICE_{self._user.username}", invoice_cache, timeout = 30*24*60*60)
                        ultimo_invoice = invoice_cache
                  except:
                        return PagamentoResult(sucesso=False)

            # DATA ATUAL E EXPIRACAO DO INVOICE
            timestamp_atual = time.time() * 1000
            timestamp_expiracao = ultimo_invoice['timestamp'] + 30 * 24 * 60 * 60 * 1000

            # VERIFICA SE EXISTE PAGAMENTO VALIDO E NAO EXPIRADO
            if ultimo_invoice['status'] == True:
                  if timestamp_atual < timestamp_expiracao: return PagamentoResult(sucesso=True)

            # BUSCA INVOICE NA LNMARKETS
            resposta = await lnm.get_deposit({'id': ultimo_invoice['id_invoice']})
            if 'success' not in resposta:
                  log_sys().error(f"Resposta Inválida Validação Invoice | {self._user.username} | {resposta}")
                  return PagamentoResult(sucesso=False)

            invoice = json.loads(resposta)

            # VERIFICA SE O DEPOSITO E PAGO E NAO EXPIRADO
            if invoice['success'] == True:
                  if timestamp_atual < timestamp_expiracao:
                        ultimo_invoice['status'] = True
                        ultimo_invoice['timestamp'] = invoice['ts']
                        cache.set(f"INVOICE_{self._user.username}", ultimo_invoice, timeout = 30 * 24 * 60 * 60)

                        # 1. Persiste usuário com invoice e grava log
                        await sync_to_async(InvoicesPagos.objects.create)(user=self._user, id_invoice=invoice['id'], timestamp=invoice['ts'], status=invoice['success'])
                        log_user(username=self._user.username).info(f"Invoice Buscado, Validado e Salvo | {invoice['id']}")

                        return PagamentoResult(sucesso=True)

            # DELETA INVOICE NAO PAGO OU EXPIRADO
            cache.delete(f"INVOICE_{self._user.username}")
            return PagamentoResult(sucesso=False)

      def _transformar_preco_em_sats(self, preco_atual_btc):
            ticket_automacao = 1
            return int((ticket_automacao / preco_atual_btc) * 100_000_000)

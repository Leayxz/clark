import requests, json, qrcode, base64, time
from io import BytesIO
from lnmarkets import rest
from decouple import config
from django.core.cache import cache
from django.contrib.auth.models import User
from infra.models import InvoicesPagos
from infra.index import log_sys, log_user

options = {"key": config("LNM_API_KEY"), "secret": config("LNM_SECRET_KEY"), "passphrase": config("LNM_PASSPHRASE"), "network": 'mainnet'}
lnm = rest.LNMarketsRest(**options)
logger_sys = log_sys()

def gerar_invoice(username) -> dict | None :

      logger_user = log_user(username)

      # VALOR ATUAL DA AUTOMACAO EM SATS
      preco_automacao = 1
      preco_atual_btc = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCBRL").json()["price"])
      preco_em_sats = int((preco_automacao / preco_atual_btc) * 100_000_000)

      # GERA INTENCAO DE COMPRA
      resposta = lnm.new_deposit({"amount": preco_em_sats})
      if 'message' in resposta: logger_sys.error(f"❌ Resposta Inválida Invoice LnMarkets: {resposta}"); return None
      intencao_compra = json.loads(resposta)

      # ARMAZENA EMAIL + ID INVOICE EM CACHE POR 30 DIAS
      invoice = {'username': username, 'id_invoice': intencao_compra['depositId'], 'timestamp': time.time() * 1000, 'status': False}
      cache.set(f"INVOICE_{username}", invoice)

      # GERA QR CODE BASE64
      qrc = qrcode.make(intencao_compra["paymentRequest"])
      buffer = BytesIO()
      qrc.save(buffer, "PNG")
      qrc_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

      logger_user.info(f"QRCode Gerado.")
      return {"qrcode": qrc_base64, 'id_invoice': intencao_compra['depositId'], 'paymenthash': intencao_compra["paymentRequest"]}

def validar_pagamento(user) -> bool:

      username = user.username
      logger_user = log_user(username)

      # BUSCA INVOICE EM CACHE E SE NAO EXISTIR TENTA NO DB
      ultimo_invoice = cache.get(f"INVOICE_{username}")
      if ultimo_invoice == None:
            try:
                  ultimo_invoice = InvoicesPagos.objects.filter(user = user).latest('timestamp')
                  invoice_cache = { 'username': username, 'id_invoice': ultimo_invoice.id_invoice, 'timestamp': ultimo_invoice.timestamp, 'status': ultimo_invoice.status }
                  cache.set(f"INVOICE_{username}", invoice_cache, timeout = 30*24*60*60)
                  ultimo_invoice = invoice_cache
            except:
                  return False

      # DATA ATUAL E EXPIRACAO DO INVOICE
      timestamp_atual = time.time() * 1000
      timestamp_expiracao = ultimo_invoice['timestamp'] + 30 * 24 * 60 * 60 * 1000

      # VERIFICA SE EXISTE PAGAMENTO VALIDO E NAO EXPIRADO
      if ultimo_invoice['status'] == True:
            if timestamp_atual < timestamp_expiracao: return True

      # BUSCA INVOICE NA LNMARKETS
      resposta = lnm.get_deposit({'id': ultimo_invoice['id_invoice']})
      if 'success' not in resposta: logger_sys.error(f"Resposta Inválida Validação Invoice | {username} | {resposta}"); return False
      invoice = json.loads(resposta)

      # VERIFICA SE O DEPOSITO E PAGO E NAO EXPIRADO
      if invoice['success'] == True:
            if timestamp_atual < timestamp_expiracao:
                  ultimo_invoice['status'] = True
                  ultimo_invoice['timestamp'] = invoice['ts']

                  cache.set(f"INVOICE_{username}", ultimo_invoice, timeout = 30 * 24 * 60 * 60)

                  # ARMAZENA USER E INVOICE PAGO NO DB
                  InvoicesPagos.objects.create(user = user, id_invoice = invoice['id'], timestamp = invoice['ts'], status = invoice['success'])
                  logger_user.info(f"Invoice Buscado, Validado e Salvo | {invoice['id']}")
                  return True

      # DELETA INVOICE NAO PAGO OU EXPIRADO
      cache.delete(f"INVOICE_{username}")
      return False

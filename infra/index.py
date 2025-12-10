import time, hmac, requests, telebot, logging, os
from django.core.cache import cache
from hashlib import sha256

def buscar_saldo(API_KEY, SECRET_KEY) -> float | None:

      headers = {"X-BX-APIKEY": API_KEY}
      params = f"timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v3/user/balance?{params}&signature={assinatura}"

      response = requests.get(url, headers = headers).json()
      if 'timestamp is invalid' in response['msg']: print(f"❌ TimeStamp Inválido: {response} | ⏳ Tentando Novamente"); return None
      elif response['msg']: print(f"❌ Saldo Inválido: {response} | ⏳ Tentando Novamente"); return None

      saldo_usuario = response['data'][0]["availableMargin"]
      return float(saldo_usuario)

def buscar_ordens(API_KEY, SECRET_KEY) -> list | None:

      params = f"timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/user/positions?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.get(url, headers = headers).json()
      if 'data' not in response: print(f"❌ Resposta Ordens Abertas Inválida: {response}"); return None

      ordens_abertas = response['data']
      return ordens_abertas

def abrir_ordem(quantity_usdt, preco_atual, API_KEY, SECRET_KEY) -> float | None:

      quantity = round(quantity_usdt / preco_atual, 4)

      params = f"symbol=BTC-USDT&side=BUY&positionSide=LONG&type=MARKET&quantity={quantity}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/trade/order?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: print(f"🚫 Ordem Não Eviada: {response['msg']}"); return None

      novo_preco_referencia = response['data']['order']['avgPrice']
      return float(novo_preco_referencia)

def fechar_ordem(positionId, API_KEY, SECRET_KEY) -> str | None:

      params = f"positionId={positionId}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v1/trade/closePosition?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: print(f"❌ Posição Não Encerrada: {response['msg']}"); return None

      return response['data']['positionId']

def injetar_margem(positionId, quantidade_injetada, API_KEY, SECRET_KEY) -> tuple[int, str] | None:

      params = f"symbol=BTC-USDT&amount={quantidade_injetada}&type=1&positionId={positionId}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/trade/positionMargin?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: print(f"❌ Margem Não Injetada: {response['msg']}"); return None

      quantidade_injetada, positionId = response['amount'], response['positionId']

      return quantidade_injetada, positionId

# PRECISO TESTAR ANTES DE JOGAR PRA MAIN
# quantidade_injetada, positionId = injetar_margem(positionId="asdsd", quantidade_injetada=123, API_KEY="asd", SECRET_KEY="asd")
# print(quantidade_injetada, positionId)

def enviar_mensagem(username, mensagem):

      user_telegram = cache.get(f"USER_TELEGRAM_{username}")
      if user_telegram == None or user_telegram['TOKEN_TELEGRAM'] == None or user_telegram['ID_TELEGRAM'] == None: return print(f"⚠️ Telegram Não Cadastrado: {username}")

      TOKEN_TELEGRAM = user_telegram['TOKEN_TELEGRAM']
      ID_TELEGRAM = user_telegram['ID_TELEGRAM']
      bot = telebot.TeleBot(TOKEN_TELEGRAM)

      try:
            bot.send_message(ID_TELEGRAM, f"{mensagem}"); return

      except Exception as erro:
            print(f"❌ Algo Errado Com o Telegram:", erro); return

def user_log(username):

      # GERA PASTA E CAMINHO PARA OS LOGS
      os.makedirs("logs", exist_ok = True)
      log_path = os.path.join("logs", f"{username}.log")

      # CRIA OU BUSCA O LOG DO USER
      logger = logging.getLogger(username)
      logger.setLevel(logging.INFO)

      # EVITA ADICIONAR VARIOS HANDLERS
      if not logger.handlers:
            formato = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            file_handler = logging.FileHandler(log_path, encoding = "UTF-8")
            file_handler.setFormatter(formato)
            logger.addHandler(file_handler)

      return logger

def limpar_compra_inf_baixo(username, config):
      if config.get('compra_inf_baixo'): del config['compra_inf_baixo']
      cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)


# PRECISO BUSCAR SALDO E ORDENS FORA DO ON_MESSAGE DEVIDO RATE LIMIT

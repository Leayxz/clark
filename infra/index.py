import time, hmac, requests, telebot, logging, os
from django.core.cache import cache
from hashlib import sha256

def buscar_saldo(API_KEY, SECRET_KEY) -> dict:

      headers = {"X-BX-APIKEY": API_KEY}
      params = f"timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v3/user/balance?{params}&signature={assinatura}"

      response = requests.get(url, headers = headers).json()
      if response['msg']: return {'saldo': None, 'msg': response['msg']}

      saldo_usuario = float(response['data'][0]["availableMargin"])
      return {'saldo': saldo_usuario, 'msg': None}

def buscar_ordens(API_KEY, SECRET_KEY) -> dict:

      params = f"timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/user/positions?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.get(url, headers = headers).json()
      if response['msg']: return {'ordens_abertas': None, 'msg': response['msg']}

      ordens_abertas = response['data']
      return {'ordens_abertas': ordens_abertas, 'msg': None}

def abrir_ordem(quantity_usdt, preco_atual, API_KEY, SECRET_KEY) -> dict:

      quantity = round(quantity_usdt / preco_atual, 4)

      params = f"symbol=BTC-USDT&side=BUY&positionSide=LONG&type=MARKET&quantity={quantity}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/trade/order?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: return {'novo_preco_referencia': '', 'msg': response['msg']}

      novo_preco_referencia = float(response['data']['order']['avgPrice'])
      return {'novo_preco_referencia': novo_preco_referencia, 'msg': ''}

def fechar_ordem(positionId, API_KEY, SECRET_KEY) -> dict:

      params = f"positionId={positionId}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v1/trade/closePosition?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: return {'positionId': '', 'msg': response['msg']}

      positionId = response['data']['positionId']
      return {'positionId': positionId, 'msg': ''}

def injetar_margem(positionId, quantidade_injetada, API_KEY, SECRET_KEY) -> dict:

      params = f"symbol=BTC-USDT&amount={quantidade_injetada}&type=1&positionId={positionId}&timestamp={int(time.time() * 1000)}"
      assinatura = hmac.new(SECRET_KEY.encode(), params.encode(), sha256).hexdigest()
      url = f"https://open-api.bingx.com/openApi/swap/v2/trade/positionMargin?{params}&signature={assinatura}"
      headers = {"X-BX-APIKEY": API_KEY}

      response = requests.post(url, headers = headers).json()
      if response['msg']: return {'quantidade_injetada': '', 'positionId': '', 'msg': response['msg']}

      return {'quantidade_injetada': response['amount'], 'positionId': response['positionId'], 'msg': ''}

# PRECISO TESTAR ANTES DE JOGAR PRA MAIN
# quantidade_injetada, positionId = injetar_margem(positionId="asdsd", quantidade_injetada=123, API_KEY="asd", SECRET_KEY="asd")
# print(quantidade_injetada, positionId)

def enviar_mensagem(username, mensagem):

      user_telegram = cache.get(f"USER_TELEGRAM_{username}")
      if user_telegram == None or user_telegram['TOKEN_TELEGRAM'] == None or user_telegram['ID_TELEGRAM'] == None: return {'msg': 'Telegram Não Cadastrado.'}

      TOKEN_TELEGRAM = user_telegram['TOKEN_TELEGRAM']
      ID_TELEGRAM = user_telegram['ID_TELEGRAM']
      bot = telebot.TeleBot(TOKEN_TELEGRAM)

      try:
            return bot.send_message(ID_TELEGRAM, f"{mensagem}")

      except Exception as erro:
            return {'msg': erro}

def log_user(username):

      # GERA PASTA E CAMINHO PARA OS LOGS
      os.makedirs("logs", exist_ok = True)
      log_path = os.path.join("logs", f"{username}.log")

      # INSTANCIA O LOGGER COM USER
      logger = logging.getLogger(username.replace('@', '_').replace('.', '_'))
      logger.setLevel(logging.INFO)

      # EVITA ADICIONAR VARIOS HANDLERS
      if not logger.handlers:

            # CONFIG PARA ONDE VAI E FORMATO
            local = logging.FileHandler(log_path, encoding = "UTF-8")
            formato = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

            # SETA CONFIG
            local.setFormatter(formato)
            logger.addHandler(local)

      return logger

def log_sys():

      # GERA PASTA E CAMINHO PARA OS LOGS
      os.makedirs("logs", exist_ok = True)
      log_path = os.path.join("logs", f"sistema.log")

      logger = logging.getLogger('sistema')
      logger.setLevel(logging.INFO)

      if not logger.handlers:
            stdout = logging.StreamHandler()
            local = logging.FileHandler(log_path, encoding = 'UTF-8')
            formato = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

            stdout.setFormatter(formato)
            local.setFormatter(formato)

            logger.addHandler(stdout)
            logger.addHandler(local)

      return logger

def limpar_compra_inf_baixo(username, config):
      
      if config.get('compra_inf_baixo'):
            del config['compra_inf_baixo']
            cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)

# PODERIA DEIXAR LOG NAS FUNÇOES, MAS NAO GOSTEI DA IDEIA DE ACOPLAR
# MELHOR RETORNAR ERRO E TRATAR NA TASK

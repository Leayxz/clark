import threading, websocket, json, gzip, io, time
from django.core.cache import cache
from infra.index import log_sys

def preco_socket():

      logger_sys = log_sys()

      def on_open(conexao):
            conexao.send(json.dumps({"id": "1", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}))
            logger_sys.info("✅ WebSocket Conectado.")

      def on_message(conexao, mensagem):
            
            # DESCOMPRIME A MENSAGEM EM GZIP/BINARIO
            compressed = gzip.GzipFile(fileobj = io.BytesIO(mensagem), mode='rb')
            resposta = compressed.read().decode('UTF-8')
            if resposta == "Ping": return conexao.send("Pong")
            mensagem = json.loads(resposta)
            if mensagem['data'] == None: return logger_sys.info(f"Resposta Websocket Inválida: {mensagem}.")

            # ACESSA MENSAGEM E SALVA PRECO EM CACHE
            preco_atual = float(mensagem["data"]["c"])
            cache.set('preco_atual', preco_atual)
            #logger_sys.info(f"Preço Atual BingX: ${preco_atual}")

            # SETA E ATUALIZA ATH
            cache.add('ultima_ath', 126_000)
            if preco_atual > cache.get('ultima_ath'): cache.set('ultima_ath', preco_atual)

      def on_error(ws, error):
            logger_sys.error(f"Erro Webscoket: {error}")
            time.sleep(3)

      def on_close(ws, close_status_code, close_msg):
            logger_sys.info(f"Conexão Fechada | Reconectando Em 3 Segundos"); time.sleep(3)
            preco_socket() # POSSIBILIDADE DE CRIAR VARIAS THREADS

      # INICIALIZA WEBSOCKET PRECO EM THREAD
      URL_PRECO = "wss://open-api-swap.bingx.com/swap-market"
      ws_app = websocket.WebSocketApp(URL_PRECO, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
      ws_thread = threading.Thread(target = ws_app.run_forever, daemon = True)
      ws_thread.start()

# WEBSOCKET RODANDO EM THREAD DEDICADA PARA NAO TRAVAR O SERVIDOR.
# PRECISO BUSCAR SALDO E ORDENS FORA DO ON_MESSAGE DEVIDO RATE LIMIT.

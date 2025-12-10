import threading, websocket, json, gzip, io, time
from django.core.cache import cache

def preco_socket():
      def on_open(conexao):
            conexao.send(json.dumps({"id": "1", "reqType": "sub", "dataType": "BTC-USDT@lastPrice"}))
            print("✅ WebSocket Conectado.")

      def on_message(conexao, mensagem):
            
            # DESCOMPRIME A MENSAGEM EM GZIP/BINARIO PARA STRING JSON
            compressed = gzip.GzipFile(fileobj = io.BytesIO(mensagem), mode='rb')
            mensagem = compressed.read().decode('UTF-8')

            # RESPONDE O PING E VALIDA RESPOSTA
            if mensagem == "Ping": conexao.send("Pong"); return #print(f"Enviando Pong!"); return
            if "BTC-USDT@lastPrice" not in mensagem: print(f"❌ Resposta Preço Inválida: {mensagem}"); return

            # ACESSA MENSAGEM E SALVA PRECO EM CACHE
            preco_atual = float(json.loads(mensagem)["data"]["c"])
            cache.set('preco_atual', preco_atual)
            #print(f"⬜ Preço Atual BingX: ${preco_atual}")

            # SETA E ATUALIZA ATH
            cache.add('ultima_ath', 126_000)
            if preco_atual > cache.get('ultima_ath'): cache.set('ultima_ath', preco_atual)

      def on_error(ws, error):
            print("❌ Algo Deu Errado:", error)
            time.sleep(3)

      def on_close(ws, close_status_code, close_msg):
            print("🔒 Conexão Fechada")
            print(f"⏳ Reconectando Em 3 Segundos"); time.sleep(3)
            preco_socket()

      # INICIALIZA WEBSOCKET PRECO
      URL_PRECO = "wss://open-api-swap.bingx.com/swap-market"
      ws_app = websocket.WebSocketApp(URL_PRECO, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
      ws_thread = threading.Thread(target = ws_app.run_forever, daemon = True)
      ws_thread.start()

# WEBSOCKET RODANDO EM THREAD DEDICADA PARA NAO TRAVAR O SERVIDOR
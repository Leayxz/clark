import time, traceback
from celery import shared_task
from dominio.services import Operacoes
from dominio.services import  enviar_mensagem_compra, enviar_mensagem_fechamento
from infra.index import  buscar_saldo, buscar_ordens, abrir_ordem, fechar_ordem, enviar_mensagem, limpar_compra_inf_baixo
from django.core.cache import cache

@shared_task
def rodar_automacao(username):

      # INSTANCIA
      op = Operacoes()
      enviar_mensagem(username, f"🎯 Automação Rodando.")

      while True:
            try:
                  # DADOS USUARIO
                  invoice = cache.get(f"INVOICE_{username}")
                  config = cache.get(f"CONFIGS_USER_{username}")
                  DADOS_API = cache.get(f"{username}_CACHE_API:")

                  # VALIDA INVOICE E API
                  if invoice == None or invoice['status'] == False: print(f"❌ Usuário {username} Sem Pagamento: {invoice} | 🚫 Encerrando Automação"); limpar_compra_inf_baixo(username, config); break
                  if DADOS_API == None: print(f"⚠️ Nenhuma API Encontrada: {username} | 🚫 Encerrando Automação"); limpar_compra_inf_baixo(username, config); break

                  # SALDO E ORDENS ABERTAS
                  start = time.time()
                  try:
                        saldo = buscar_saldo(DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                  except:
                        print(f"❌ ERRO DE CONEXÃO SALDO: {saldo}")
                        saldo = None
                  try:
                        ordens_abertas = buscar_ordens(DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                  except:
                        print(f"❌ ERRO DE CONEXÃO ORDENS")
                        ordens_abertas = None
                  temp_req = time.time() - start

                  if saldo == None: print(f"❌ Resposta Saldo Task Inválida: {saldo} | ⏳ Tentando Novamente"); continue
                  if ordens_abertas == None: print(f"❌ Resposta Ordens Task Inválida: {ordens_abertas} | ⏳ Tentando Novamente"); continue

                  ################################################ ABRINDO ORDENS ################################################

                  # VERIFICA ULTIMA ATH E PRECO ATUAL
                  ultima_ath = cache.get('ultima_ath')
                  preco_atual = cache.get('preco_atual')
                  if preco_atual == None: print(f"⚠️ Falha Ao Ler Preço: {preco_atual} | ⏳ Tentando Em 4 Segundos"); time.sleep(4); continue

                  resposta, quantity = op.condicao_compra(preco_atual, saldo, config)

                  if resposta:
                        if resposta == 'COMPRA SUBINDO':
                              preco_compra = abrir_ordem(quantity, preco_atual, DADOS_API['API_KEY'], DADOS_API['SECRET_KEY'])
                              config['preco_referencia'] = preco_compra

                        elif resposta == 'COMPRA DESCENDO':
                              preco_compra = abrir_ordem(quantity, preco_atual, DADOS_API['API_KEY'], DADOS_API['SECRET_KEY'])
                              config['compra_inf_baixo'] = preco_compra

                        enviar_mensagem_compra(username, preco_compra, preco_atual, ultima_ath)

                  ################################################ FECHANDO ORDENS ################################################

                  for ordem in ordens_abertas:

                        valor_fechamento, lucro = op.condicao_fechamento(ordem, config)
                        if valor_fechamento:
                              if preco_atual >= valor_fechamento:
                                    fechar_ordem(ordem['positionId'], DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                                    config['compra_inf_baixo'] = valor_fechamento
                                    enviar_mensagem_fechamento(username, lucro, ordem)

                  # INJETANDO MARGEM

                  cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)
                  print(f"✅ Automação Ativa Para: {username} | Tempo: {temp_req:.2f} | Saldo: {saldo}")
                  time.sleep(1.5)

            except Exception as erro:
                  cache.delete(f"{username}_CACHE_API:")
                  config['id_task'] = False
                  cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)
                  print(f"🚫 Automação Encerrada: {erro}")
                  print(traceback.format_exc())

                  limpar_compra_inf_baixo(username, config)
                  enviar_mensagem(username, f"🚫 Automação Encerrada")
                  break

# PRECISO LIMPAR TODA COMPRA_INF_BAIXO PORQUE SENAO QUANDO O USER MUDAR O PRECO_REFERENCIA, COMPRA_INF_BAIXO AINDA VAI SER O ANTIGO
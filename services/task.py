import time, traceback
from celery import shared_task
from dominio.operacoes import Operacao
from infra.index import  buscar_saldo, buscar_ordens, abrir_ordem, fechar_ordem, enviar_mensagem, limpar_compra_inf_baixo, log_user, log_sys
from django.core.cache import cache

@shared_task
def rodar_automacao(username):

      # INSTANCIAS
      logger_sys = log_sys()
      logger_user = log_user(username)
      enviar_mensagem(username, f"🎯 Automação Rodando.")

      while True:
            try:
                  # DADOS USUARIO
                  invoice = cache.get(f"INVOICE_{username}")
                  config = cache.get(f"CONFIGS_USER_{username}")
                  DADOS_API = cache.get(f"{username}_CACHE_API:")

                  # VALIDA INVOICE E API
                  if invoice == None or invoice['status'] == False: logger_sys.info(f"❌ Usuário {username} sem pagamento: {invoice} | 🚫 Encerrando automação"); limpar_compra_inf_baixo(username, config); break
                  if DADOS_API == None: logger_sys.info(f"⚠️ Nenhuma API encontrada para: {username} | 🚫 Encerrando automação"); limpar_compra_inf_baixo(username, config); break

                  # SALDO E ORDENS ABERTAS
                  start = time.time()
                  saldo = buscar_saldo(DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                  ordens_abertas = buscar_ordens(DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                  temp_req = time.time() - start

                  if saldo['msg']: print(f"❌ Resposta Saldo Task Inválida: {saldo} | ⏳ Tentando Novamente"); continue
                  if ordens_abertas['msg']: print(f"❌ Resposta Ordens Task Inválida: {ordens_abertas} | ⏳ Tentando Novamente"); continue

                  ################################################ ABRINDO ORDENS ################################################

                  # VERIFICA ULTIMA ATH E PRECO ATUAL
                  ultima_ath = cache.get('ultima_ath')
                  preco_atual = cache.get('preco_atual')
                  op = Operacao(config=config, ordem=ordens_abertas, preco_atual=preco_atual, saldo=saldo)

                  if preco_atual == None: logger_sys.warning(f"⚠️ Falha ao ler preço: {preco_atual} | ⏳ Tentando novamente em 3 segundos"); continue

                  confirmacao_compra, tamanho_mao, direcao = op.avaliar_compra(preco_atual, saldo, config)
                  if confirmacao_compra:
                        preco_compra = abrir_ordem(tamanho_mao, preco_atual, DADOS_API['API_KEY'], DADOS_API['SECRET_KEY'])
                        if direcao == 'SUBINDO': config['preco_referencia'] = preco_compra
                        elif direcao == 'DESCENDO': config['compra_inf_baixo'] = preco_compra

                        percentual_queda = ((ultima_ath - preco_atual) / ultima_ath) * 100
                        logger_user.info(f"🟡 Compra Realizada: ${preco_compra} | 🔶 ATH: {percentual_queda:.2f}%")
                        enviar_mensagem(username, f"🟡 Compra Realizada: ${preco_compra} | 🔶 ATH: {percentual_queda:.2f}%")

                  ################################################ FECHANDO ORDENS ################################################

                  for ordem in ordens_abertas['ordens_abertas']:

                        confirmação_fechamento, valor_fechamento = op.avaliar_venda(preco_atual, ordem, config)
                        if confirmação_fechamento:
                              fechar_ordem(ordem['positionId'], DADOS_API["API_KEY"], DADOS_API["SECRET_KEY"])
                              config['compra_inf_baixo'] = valor_fechamento
                              logger_user.info(f"🤑 Ordem Fechada: {ordem['positionId']} | {username} | Lucro: ${float(ordem['unrealizedProfit'])}")
                              enviar_mensagem(username, f"🤑 Ordem Fechada | Lucro: ${float(ordem['unrealizedProfit'])}")

                  # INJETANDO MARGEM

                  cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)
                  print(f"✅ Automação Ativa Para: {username} | Tempo: {temp_req:.2f} | Saldo: {saldo}")
                  time.sleep(1.5)

            except Exception as erro: # REMOVER PRINTS E REFATORAR
                  cache.delete(f"{username}_CACHE_API:")
                  config['id_task'] = False
                  cache.set(f"CONFIGS_USER_{username}", config, timeout=30*24*60*60)
                  print(f"🚫 Automação Encerrada: {erro}")
                  print(traceback.format_exc())

                  limpar_compra_inf_baixo(username, config)
                  enviar_mensagem(username, f"🚫 Automação Encerrada")
                  break

# PRECISO LIMPAR TODA COMPRA_INF_BAIXO PORQUE SENAO QUANDO O USER MUDAR O PRECO_REFERENCIA, COMPRA_INF_BAIXO AINDA VAI SER O ANTIGO
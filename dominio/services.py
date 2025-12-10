from infra.index import enviar_mensagem

class Operacoes():
      def condicao_compra(self, preco_atual, saldo, config) -> tuple[str | None, int | None]:

            # DEFINE TAMANHO DA MÃO BASEADO NO PREÇO
            if preco_atual >= 115_000: quantity = config['quantity1']
            elif 110_000 <= preco_atual < 115_000: quantity = config['quantity2']
            elif 105_000 <= preco_atual < 110_000: quantity = config['quantity3']
            elif preco_atual <= 104_999: quantity = config['quantity4']

            # DEFINE CONFIGURAÇOES DO USER
            preco_referencia = config['preco_referencia']
            compra_inf_baixo = config.get('compra_inf_baixo') or config['preco_referencia']
            variacao_compra = config['variacao_compra']
            comprar_abaixo = config['comprar_abaixo']
            limite_margem = config['limite_margem']
            min_dolar = 2

            condicao_compra_inf_cima = (saldo > min_dolar and saldo > limite_margem and preco_atual < comprar_abaixo and preco_atual >=  preco_referencia + variacao_compra)
            condicao_compra_inf_baixo = (saldo > min_dolar and saldo > limite_margem and preco_atual < comprar_abaixo and preco_atual <= compra_inf_baixo - variacao_compra)

            if condicao_compra_inf_cima:
                  return "COMPRA SUBINDO", quantity

            elif condicao_compra_inf_baixo:
                  return "COMPRA DESCENDO", quantity

            # SEM CONDICAO, APENAS RETORNA      
            return None, None

      def condicao_fechamento(self, ordem, config):
            preco_entrada = float(ordem['avgPrice'])
            percentual_lucro = config['percentual_lucro'] / 100
            taxa = abs(float(ordem['realisedProfit']))
            lucro = float(ordem['unrealizedProfit'])                       
            valor_fechamento = preco_entrada + (preco_entrada * percentual_lucro) + taxa

            return float(valor_fechamento), lucro

def enviar_mensagem_compra(username, preco_compra, preco_atual, ultima_ath):
      percentual_queda = ((ultima_ath - preco_atual) / ultima_ath) * 100
      print(f"🟡 Compra Realizada: ${preco_compra} | 🔶 ATH: {percentual_queda:.2f}%")
      enviar_mensagem(username, f"🟡 Compra Realizada: ${preco_compra}\n🔶 ATH: {percentual_queda:.2f}%")

def enviar_mensagem_fechamento(username, lucro, ordem):
      print(f"🤑 Ordem Fechada: {ordem['positionId']} | {username} | Lucro: ${lucro}")
      enviar_mensagem(username, f"🤑 Ordem Fechada | Lucro: ${lucro}")

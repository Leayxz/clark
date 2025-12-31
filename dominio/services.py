class Operacoes():
      def avaliar_venda(self, preco_atual, ordem, config) -> tuple[bool, float | None]:
            preco_entrada = float(ordem['avgPrice'])
            percentual_lucro = config['percentual_lucro'] / 100
            taxa = abs(float(ordem['realisedProfit']))
            valor_fechamento = preco_entrada + (preco_entrada * percentual_lucro) + taxa

            if preco_atual >= valor_fechamento: return True, valor_fechamento
            return False, None

      def avaliar_compra(self, preco_atual, saldo, config) -> tuple[bool, int | None, str | None]:
            direcao = self._condicao_compra(preco_atual, saldo, config)
            if direcao:
                  tamanho_mao = self._define_valor_mao(preco_atual, config)
                  return True, tamanho_mao, direcao

            return False, None, None
      
      def _define_valor_mao(self, preco_atual, config) -> int:
            
            if preco_atual >= 115_000: return config['quantity1']
            if preco_atual >= 110_000: return config['quantity2']
            if preco_atual >= 105_000: return config['quantity3']
            return config['quantity4']

      def _condicao_compra(self, preco_atual, saldo, config) -> str | None:

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
                  return 'SUBINDO' # REMOVER STRING MAGICA 

            elif condicao_compra_inf_baixo:
                  return 'DESCENDO' # REMOVER STRING MAGICA

            return None

# ENTIDADE STATELESS PORQUE NAO TENHO NECESSIDADE DE GUARDAR ESTADO DO USUARIO, ENTAO TUDO E PASSADO NO METODO

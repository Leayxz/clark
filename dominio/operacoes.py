from dataclasses import dataclass

@dataclass
class ResultCompra:
    sucesso: bool
    tamanho_mao: int | None
    direcao: str | None

@dataclass
class ResultVenda:
    sucesso: bool
    valor_fechamento: float | None

class Operacao:

      def __init__(self, preco_atual, saldo, ordem, config):
            self._preco_atual = preco_atual
            self._saldo = saldo
            self._ordem = ordem
            self._config = config

      def avaliar_compra(self) -> ResultCompra:
            direcao = self._condicao_compra()

            if direcao:
                  tamanho_mao = self._define_valor_mao()
                  return ResultCompra(True, tamanho_mao, direcao)

            return ResultCompra(False, None, None)

      def avaliar_venda(self) -> ResultVenda:
            preco_entrada = float(self._ordem['avgPrice'])
            percentual_lucro = self._config['percentual_lucro'] / 100
            taxa = abs(float(self._ordem['realisedProfit']))
            valor_fechamento = preco_entrada + (preco_entrada * percentual_lucro) + taxa

            if self._preco_atual >= valor_fechamento: return ResultVenda(True, valor_fechamento)
            return ResultVenda(False, None)

      def _define_valor_mao(self) -> int:

            if self._preco_atual >= 115_000: return self._config['quantity1']
            if self._preco_atual >= 110_000: return self._config['quantity2']
            if self._preco_atual >= 105_000: return self._config['quantity3']
            return self._config['quantity4']

      def _condicao_compra(self) -> str | None:

            # DEFINE CONFIGURAÇOES DO USER
            preco_referencia = self._config['preco_referencia']
            compra_inf_baixo = self._config.get('compra_inf_baixo') or self._config['preco_referencia']
            variacao_compra = self._config['variacao_compra']
            comprar_abaixo = self._config['comprar_abaixo']
            limite_margem = self._config['limite_margem']
            min_dolar = 2

            condicao_compra_inf_cima = (self._saldo > min_dolar and self._saldo > limite_margem and self._preco_atual < comprar_abaixo and self._preco_atual >=  preco_referencia + variacao_compra)
            condicao_compra_inf_baixo = (self._saldo > min_dolar and self._saldo > limite_margem and self._preco_atual < comprar_abaixo and self._preco_atual <= compra_inf_baixo - variacao_compra)

            if condicao_compra_inf_cima:
                  return 'SUBINDO' # REMOVER STRING MAGICA 

            elif condicao_compra_inf_baixo:
                  return 'DESCENDO' # REMOVER STRING MAGICA

            return None

# ESTOU REJEITANDO CONSCIENTEMENTE O USO DE VOs POR ENQUANTO.

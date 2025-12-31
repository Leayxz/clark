from dominio.services import Operacoes

op = Operacoes()

def test_compra_subindo():
      config = {"quantity1": 10, "quantity2": 8, "quantity3": 5, "quantity4": 3, "preco_referencia": 110_000, "variacao_compra": 500, "comprar_abaixo": 120_000, "limite_margem": 5}
      confirmacao_compra, tamanho_mao, direcao = op.avaliar_compra(preco_atual = 111_000, saldo = 100, config = config)

      assert direcao == "SUBINDO" and tamanho_mao == 8

def test_comprar_descendo():
      config = {"quantity1": 10, "quantity2": 8, "quantity3": 5, "quantity4": 3, "preco_referencia": 110_000, "compra_inf_baixo": 108_000, "variacao_compra": 500, "comprar_abaixo": 120_000, "limite_margem": 5}
      confirmacao_compra, tamanho_mao, direcao = op.avaliar_compra(preco_atual = 107_000, saldo = 100, config = config)

      assert direcao == "DESCENDO" and tamanho_mao == 5

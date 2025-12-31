from unittest.mock import patch, MagicMock
from infra.index import buscar_saldo, buscar_ordens, abrir_ordem, fechar_ordem, enviar_mensagem

@patch("infra.index.requests.get")
def test_buscar_saldo(mock_get):
      mock_get.return_value.json.return_value = {"msg": None, "data": [{"availableMargin": "1234.56"}]}
      result = buscar_saldo("fake_api", "fake_secret")

      assert type(result) == dict, "Resultado Deve Ser Dict"
      assert result['saldo'] == 1234.56, "Resultado Inválido"

@patch("infra.index.requests.get")
def test_buscar_ordens(mock_get):

      mock_get.return_value.json.return_value = {'msg': None, 'data': [{'ordem1': 'ordem1'}]}
      resultado = buscar_ordens('FAKE_API', 'FAKE_SECRET')

      assert type(resultado) == dict, "Resultado Deve Ser Uma Dict"
      assert resultado['ordens_abertas'], "Resultado Deve Conter Um Elemento"

@patch("infra.index.requests.post")
def test_abrir_ordem(mock_post):
      mock_post.return_value.json.return_value = {'msg': None, 'data': {'order': {'avgPrice': 12345.67}}}
      resultado = abrir_ordem(100, 120_000, 'FAKE', 'FAKE')

      assert type(resultado) == dict, "Resultado Não Dict"
      assert resultado['novo_preco_referencia'] == 12345.67, "Resultado Inválido"

@patch("infra.index.requests.post")
def test_fechar_ordem(mock_post):

      mock_post.return_value.json.return_value = {'msg': None, 'data': {'positionId': '123456789'}}
      resultado = fechar_ordem('123456789', 'FAKE', 'FAKE')

      assert type(resultado) == dict, "Resultado Não É Uma String"
      assert resultado['positionId'] == '123456789'

@patch("infra.index.telebot.TeleBot")
@patch("infra.index.cache.get")
def test_enviar_mensagem(mock_cache_get, mock_telebot):

      mock_cache_get.return_value = {'TOKEN_TELEGRAM': 'FAKE', 'ID_TELEGRAM': '123456'}
      mock_bot = MagicMock()
      mock_telebot.return_value = mock_bot

      enviar_mensagem("Leandro", 'Olá, Mundo!')
      mock_telebot.assert_called_once_with("FAKE")
      mock_bot.send_message.assert_called_once_with('123456', 'Olá, Mundo!')

from unittest.mock import patch, MagicMock
from infra.index import buscar_saldo, buscar_ordens, abrir_ordem, fechar_ordem, enviar_mensagem

@patch("infra.index.requests.get")
def test_buscar_saldo(mock_get):
      mock_get.return_value.json.return_value = {"msg": "", "data": [{"availableMargin": "1234.56"}]}
      result = buscar_saldo("fake_api", "fake_secret")

      assert type(result) == float, "Resultado Deve Ser Float"
      assert result == 1234.56, "Resultado Inválido"

@patch("infra.index.requests.get")
def test_buscar_ordens(mock_get):

      mock_get.return_value.json.return_value = {'data': [{'ordem1': 'ordem1'}]}
      resultado = buscar_ordens('FAKE_API', 'FAKE_SECRET')

      assert type(resultado) == list, "Resultado Deve Ser Uma Lista"
      assert resultado[0], "Resultado Deve Conter Um Elemento"

@patch("infra.index.requests.post")
def test_abrir_ordem(mock_post):
      mock_post.return_value.json.return_value = {'msg': '', 'data': {'order': {'avgPrice': 12345.67}}}
      resultado = abrir_ordem(100, 120_000, 'FAKE', 'FAKE')

      assert type(resultado) == float, "Resultado Não Float"
      assert resultado == 12345.67, "Resultado Inválido"

@patch("infra.index.requests.post")
def test_fechar_ordem(mock_post):

      mock_post.return_value.json.return_value = {'msg': '', 'data': {'positionId': '123456789'}}
      resultado = fechar_ordem('123456789', 'FAKE', 'FAKE')

      assert type(resultado) == str, "Resultado Não É Uma String"
      assert resultado.isdigit(), "Resultado Não É Apenas Numérico"
      assert resultado == '123456789'

@patch("infra.index.telebot.TeleBot")
@patch("infra.index.cache.get")
def test_enviar_mensagem(mock_cache_get, mock_telebot):

      mock_cache_get.return_value = {'TOKEN_TELEGRAM': 'FAKE', 'ID_TELEGRAM': '123456'}
      mock_bot = MagicMock()
      mock_telebot.return_value = mock_bot

      enviar_mensagem("Leandro", 'Olá, Mundo!')
      mock_telebot.assert_called_once_with("FAKE")
      mock_bot.send_message.assert_called_once_with('123456', 'Olá, Mundo!')

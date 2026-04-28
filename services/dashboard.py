from datetime import datetime
from web.forms import TelegramForm, AutomacaoForm
from infra.pagamentos import Pagamento
from django.core.cache import cache
from dataclasses import dataclass
from services.configuracoes import ConfigAutomacao
from telegram import Telegram

@dataclass
class DashboardResult:
      preco_atual: float
      pagamento_confirmado: bool
      configuracoes = str
      data_expiracao: datetime | None
      telegram: str | None

class Dashboard:

      def __init__(self, dados_telegram: TelegramForm, dados_automacao: AutomacaoForm, user):
            self._dados_telegram = dados_telegram
            self._dados_automacao = dados_automacao
            self._user = user

      async def inicializar_dashboard(self):

            # 1. Todas as informações necessárias para a construção do HTML
            preco_atual = cache.get("preco_atual") # Vem do cache, talvez mudar?
            pagamento = await Pagamento(user=self._user).validar_invoice()
            data_expiracao = self._data_expiracao_invoice(pagamento=pagamento)
            configuracoes = ConfigAutomacao(dados_automacao=self._dados_automacao, username=self._user.username).buscar_configuracoes()
            telegram = Telegram(username=self._user.username, dados=self._dados_telegram).buscar_telegram()

            return DashboardResult(preco_atual=preco_atual, pagamento_confirmado=pagamento.sucesso, configuracao=configuracoes, data_expiracao=data_expiracao, telegram=telegram) # debt: resolver pylance

      def _data_expiracao_invoice(self, pagamento) -> datetime | None:
            "Calcula a data de expiração do invoice."

            if not pagamento.sucesso: return None
            invoice = cache.get(f"INVOICE_{self._user.username}") # TALVEZ ISSO AQUI QUEBRE POR NAO EXISTIR INVOICE?
            data_expiracao_timestamp = (invoice["timestamp"] / 1000) + 30*24*60*60
            data_expiracao = datetime.fromtimestamp(data_expiracao_timestamp)

            return data_expiracao

# PRECISO ABSTRAIR TODA A INFRA DO SERVICE USANDO INTERFACES DE PREFERENCIA (Inversão de Dependência)
from django.core.cache import cache
from infra.index import log_user
from web.forms import AutomacaoForm

class ConfigAutomacao:

      def __init__(self, username, dados_automacao: AutomacaoForm | None = None) -> None:
            self._username = username
            self._dados = dados_automacao
            
      def buscar_configuracoes(self):
            configuracoes = cache.get(f"CONFIGS_USER_{self._username}") # debt: interface?
            if not configuracoes:
                  configuracoes = {"id_task": False, "quantity1": 0, "quantity2": 0, "quantity3": 0, "quantity4": 0, "preco_referencia": 0, 'comprar_abaixo': 0, "limite_margem": 0, "percentual_lucro": 0.0, "variacao_compra": 0, "percentual_seguranca_liquidacao": 0.0}
                  cache.set(f"CONFIGS_USER_{self._username}", configuracoes, timeout = 30*24*60*60)
            return configuracoes

      def salvar_configuracoes(self):
            cache.set(f"CONFIGS_USER_{self._username}", self._dados, timeout = 30*24*60*60) # Debt: Interface?
            log_user(self._username).info(f"✅ Novas configurações salvas para automação.") # Debt: Interface?

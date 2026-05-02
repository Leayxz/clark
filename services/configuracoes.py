from dataclasses import dataclass
from web.forms import AutomacaoForm

DEFAULT_CONFIGS = {"id_task": False, "quantity1": 0, "quantity2": 0, "quantity3": 0, "quantity4": 0, "preco_referencia": 0, 'comprar_abaixo': 0, "limite_margem": 0, "percentual_lucro": 0.0, "variacao_compra": 0, "percentual_seguranca_liquidacao": 0.0}

@dataclass
class ConfigAutomacaoResult:
      configuracoes: dict

class ConfigAutomacao:
      "Classe responsável por gerenciar o estado das configurações de automação do usuário."

      def __init__(self, cache, log_user) -> None:
            self._cache = cache
            self._log_user = log_user

      def buscar_configuracoes(self, username):
            configuracoes = self._cache.get(f"CONFIGS_USER_{username}")
            if not configuracoes:
                  configuracoes = DEFAULT_CONFIGS
                  self._cache.set(f"CONFIGS_USER_{username}", configuracoes, timeout = 30*24*60*60)
            return ConfigAutomacaoResult(configuracoes=configuracoes)

      def salvar_configuracoes(self, username, dados_automacao: AutomacaoForm):
            self._cache.set(f"CONFIGS_USER_{username}", dados_automacao, timeout = 30*24*60*60)
            self._log_user(username).info(f"✅ Novas configurações salvas para automação.")

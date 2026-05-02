from dataclasses import dataclass
from web.forms import TelegramForm

@dataclass
class TelegramResult:
      dados_telegram: dict

class Telegram:
      "Classe responsável por gerenciar as informações do Telegram do usuário."

      def __init__(self, cache, log_user) -> None:
            self._cache = cache
            self._log_user = log_user

      def salvar_telegram(self, username, dados: TelegramForm):
            self._cache.set(f"USER_TELEGRAM_{username}", dados, timeout=30*24*60*60)
            self._log_user(username).info(f"✅ Telegram Salvo.")

      def buscar_telegram(self, username):
            return TelegramResult(dados_telegram=self._cache.get(f"USER_TELEGRAM_{username}"))

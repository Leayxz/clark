from web.forms import TelegramForm
from django.core.cache import cache
from infra.index import log_user

class Telegram:

      def __init__(self, username, dados: TelegramForm) -> None:
            self._username = username
            self._dados = dados

      def salvar_telegram(self):
            cache.set(f"USER_TELEGRAM_{self._username}", self._dados, timeout=30*24*60*60)
            log_user(self._username).info(f"✅ Telegram Salvo.")

      def buscar_telegram(self):
            return cache.get(f"USER_TELEGRAM_{self._username}")

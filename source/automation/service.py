from .interfaces import AutomationProtocol
from ..dtos import ConfigurationDTO, ApiDTO
from ..events import AutomationEvent, Channel


class AutomationService:

    def __init__(self, repository: AutomationProtocol) -> None:
        self._repository = repository


    def get_automation_overview(self, exchange: str, email: str) -> tuple[ConfigurationDTO, ApiDTO, bool]:
        configuration = self._repository.get_configuration(exchange, email)
        api = self._repository.get_api(exchange, email)
        automation_status = self._repository.get_status_automation(exchange, email)
        return configuration, api, automation_status


    def enable_automation(self, exchange: str, email: str) -> None:
        """Ativa a automação publicando evento para o websocket começar a coletar/usar dados do usuário na exchange."""
        self._repository.add_activated_automation(exchange, email)
        payload = {"type": AutomationEvent.STARTED, "email": email, "exchange": exchange}
        self._repository.publish_event(Channel.AUTOMATION, payload)


    def disable_automation(self, exchange: str, email: str) -> None:
        """Desativa a automação publicando evento para o webscoket parar de coletar/usar dados do usuário na exchange."""
        self._repository.remove_activated_automation(exchange, email)
        payload = {"type": AutomationEvent.STOPPED, "email": email, "exchange": exchange}
        self._repository.publish_event(Channel.AUTOMATION, payload)


    def save_api(self, exchange, email: str, api: ApiDTO):
        self._repository.save_api(exchange, email, api)


    def save_configuration(self, exchange, email: str, configuration: ConfigurationDTO):
        cached_config = self._repository.get_configuration(exchange, email)
        cached_config.marginUSD =  configuration.marginUSD
        cached_config.leverage = configuration.leverage
        cached_config.buy_variation = configuration.buy_variation
        cached_config.percentage_profit = configuration.percentage_profit
        self._repository.save_configuration(exchange, email, configuration)

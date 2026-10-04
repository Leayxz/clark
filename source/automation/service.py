from .interfaces import AutomationProtocol
from ..dtos import ConfigurationDTO, ApiDTO
from ..events import AutomationEvent, Channel


class AutomationService:

    def __init__(self, repository: AutomationProtocol) -> None:
        self._repository = repository


    def get_automation_overview(self, exchange: str, user_id: str) -> tuple[ConfigurationDTO, ApiDTO, bool]:
        configuration = self._repository.get_configuration(exchange, user_id)
        api = self._repository.get_api(exchange, user_id)
        automation_status = self._repository.get_status_automation(exchange, user_id)
        return configuration, api, automation_status


    def enable_automation(self, exchange: str, user_id: str) -> None:
        """Ativa a automação publicando evento para o websocket começar a coletar/usar dados do usuário na exchange."""
        self._repository.add_activated_automation(exchange, user_id)
        payload = {"type": AutomationEvent.STARTED, "user_id": user_id, "exchange": exchange}
        self._repository.publish_event(Channel.AUTOMATION, payload)


    def disable_automation(self, exchange: str, user_id: str) -> None:
        """Desativa a automação publicando evento para o websocket parar de coletar/usar dados do usuário na exchange."""
        self._repository.remove_activated_automation(exchange, user_id)
        payload = {"type": AutomationEvent.STOPPED, "user_id": user_id, "exchange": exchange}
        self._repository.publish_event(Channel.AUTOMATION, payload)


    def save_api(self, exchange, user_id: str, api: ApiDTO):
        self._repository.save_api(exchange, user_id, api)


    def save_configuration(self, exchange, user_id: str, configuration: ConfigurationDTO):
        self._repository.save_configuration(exchange, user_id, configuration)

import redis, json
from decimal import Decimal
from typing import cast
from dataclasses import asdict

from .interfaces import AutomationProtocol
from ..dtos import ConfigurationDTO, ApiDTO
from ..constants import CacheKeys


class AutomationRepository(AutomationProtocol):

    def __init__(self, client: redis.Redis):
        self._client = client


    def add_activated_automation(self, exchange: str, user_id: str):
        payload = {"exchange": exchange, "user_id": user_id}
        self._client.sadd(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))


    def get_configuration(self, exchange: str, user_id: str) -> ConfigurationDTO:
        # json não suporta decimal e portanto deve ser convertido para Decimal quando buscar
        bytes_config = cast(bytes, self._client.get(f"{CacheKeys.LNMCONFIGURATION}:{user_id}"))
        if not bytes_config: return ConfigurationDTO()

        dict_config = json.loads(bytes_config)
        payload = {"wallet_balance": Decimal(dict_config['wallet_balance']),
                   "marginUSD": dict_config['marginUSD'],
                   "leverage": dict_config['leverage'],
                   "percentage_profit": Decimal(dict_config['percentage_profit']),
                   "buy_variation": Decimal(dict_config['buy_variation']),
                   "last_buy_up": Decimal(dict_config['last_buy_up']),
                   "last_buy_down": Decimal(dict_config['last_buy_down'])}

        return ConfigurationDTO(**payload)


    def get_status_automation(self, exchange: str, user_id: str) -> bool:
        payload = {"exchange": exchange, "user_id": user_id}
        automation = self._client.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
        return True if automation else False


    def get_api(self, exchange: str, user_id: str) -> ApiDTO:
        api = cast(bytes | None, self._client.get(f"{CacheKeys.LNMCREDENTIALS}:{user_id}"))
        return ApiDTO(**json.loads(api)) if api else ApiDTO()


    def save_api(self, exchange, user_id, api_data: ApiDTO):
        api = json.dumps(asdict(api_data))
        self._client.set(f"{CacheKeys.LNMCREDENTIALS}:{user_id}", api, CacheKeys.THIRTY_DAYS_IN_SECONDS)


    def save_configuration(self, exchange, user_id: str, configuration: ConfigurationDTO) -> None:
        # json não suporta decimal e portanto deve ser convertido para string quando salvar
        payload = {"wallet_balance": str(configuration.wallet_balance),
                   "marginUSD": configuration.marginUSD,
                   "leverage": configuration.leverage,
                   "percentage_profit": str(configuration.percentage_profit),
                   "buy_variation": str(configuration.buy_variation),
                   "last_buy_up": str(configuration.last_buy_up),
                   "last_buy_down": str(configuration.last_buy_down)}

        self._client.set(f"{CacheKeys.LNMCONFIGURATION}:{user_id}", json.dumps(payload), CacheKeys.THIRTY_DAYS_IN_SECONDS)


    def remove_activated_automation(self, exchange: str, user_id: str):
        payload = {"exchange": exchange, "user_id": user_id}
        self._client.srem(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))


    def publish_event(self, channel, payload) -> None:
        self._client.publish(channel, json.dumps(payload))

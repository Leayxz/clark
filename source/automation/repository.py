import redis, json
from decimal import Decimal
from typing import cast

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
        # a configuracao vive em um hash por exchange, compartilhado com o websocket
        configuration = cast(dict[str, str], self._client.hgetall(f"{CacheKeys.AUTOMATION_CONFIGURATION}:{exchange}:{user_id}"))
        if not configuration: return ConfigurationDTO(exchange=exchange)

        payload = {"wallet_balance": Decimal(configuration.get("wallet_balance", "0")),
                   "marginUSD": int(configuration.get("marginUSD", 0)),
                   "leverage": int(configuration.get("leverage", 0)),
                   "percentage_profit": Decimal(configuration.get("percentage_profit", "0")),
                   "buy_variation": Decimal(configuration.get("buy_variation", "0")),
                   "last_buy_up": Decimal(configuration.get("last_buy_up", "0")),
                   "last_buy_down": Decimal(configuration.get("last_buy_down", "0")),
                   "exchange": exchange}

        return ConfigurationDTO(**payload)


    def get_status_automation(self, exchange: str, user_id: str) -> bool:
        payload = {"exchange": exchange, "user_id": user_id}
        automation = self._client.sismember(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))
        return True if automation else False


    def get_api(self, exchange: str, user_id: str) -> ApiDTO:
        credentials = cast(dict[str, str], self._client.hgetall(f"{CacheKeys.AUTOMATION_CREDENTIALS}:{exchange}:{user_id}"))
        if not credentials: return ApiDTO()

        return ApiDTO(API_KEY=credentials.get("API_KEY"),
                      API_SECRET=credentials.get("API_SECRET"),
                      API_PASSPHRASE=credentials.get("API_PASSPHRASE"),
                      exchange=credentials.get("EXCHANGE") or exchange)


    def save_api(self, exchange, user_id, api_data: ApiDTO):
        # hset preserva os campos que nao vierem no payload
        key = f"{CacheKeys.AUTOMATION_CREDENTIALS}:{exchange}:{user_id}"
        self._client.hset(key, mapping={"EXCHANGE": exchange,
                                        "API_KEY": api_data.API_KEY or "",
                                        "API_SECRET": api_data.API_SECRET or "",
                                        "API_PASSPHRASE": api_data.API_PASSPHRASE or ""})
        self._client.expire(key, CacheKeys.THIRTY_DAYS_IN_SECONDS)


    def save_configuration(self, exchange, user_id: str, configuration: ConfigurationDTO) -> None:
        # apenas os campos que o formulario gerencia; wallet_balance e as refs de compra
        # pertencem ao websocket e sobrevivem porque o hset so sobrescreve o que recebe
        key = f"{CacheKeys.AUTOMATION_CONFIGURATION}:{exchange}:{user_id}"
        payload = {"marginUSD": configuration.marginUSD,
                   "leverage": configuration.leverage,
                   "percentage_profit": str(configuration.percentage_profit),
                   "buy_variation": str(configuration.buy_variation)}

        self._client.hset(key, mapping=payload)
        self._client.expire(key, CacheKeys.THIRTY_DAYS_IN_SECONDS)


    def remove_activated_automation(self, exchange: str, user_id: str):
        payload = {"exchange": exchange, "user_id": user_id}
        self._client.srem(f"{CacheKeys.ALL_ACTIVATED_AUTOMATION}", json.dumps(payload))


    def publish_event(self, channel, payload) -> None:
        self._client.publish(channel, json.dumps(payload))

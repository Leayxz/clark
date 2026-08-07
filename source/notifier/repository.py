import redis, json
from typing import cast
from dataclasses import asdict
from ..dtos import NotifierDTO
from ..constants import CacheKeys


class NotifierRepository:

    def __init__(self, client: redis.Redis) -> None:
        self._client = client


    def get_notifier(self, email: str) -> NotifierDTO:
        notifier = cast(bytes | None, self._client.get(f"notifier_telegram:{email}"))
        return NotifierDTO(**json.loads(notifier)) if notifier else NotifierDTO()


    def save_notifier(self, email: str, notifier: NotifierDTO) -> None:
        self._client.set(f"notifier_telegram:{email}", json.dumps(asdict(notifier)), CacheKeys.THIRTY_DAYS_IN_SECONDS)

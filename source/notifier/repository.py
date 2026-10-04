import redis, json
from uuid import UUID
from typing import cast
from dataclasses import asdict

from ..dtos import NotifierDTO
from ..constants import CacheKeys


class NotifierRepository:

    def __init__(self, client: redis.Redis) -> None:
        self._client = client


    def get_notifier(self, user_id: UUID) -> NotifierDTO:
        notifier = cast(bytes | None, self._client.get(f"{CacheKeys.NOTIFIER_TELEGRAM}:{user_id}"))
        return NotifierDTO(**json.loads(notifier)) if notifier else NotifierDTO()


    def save_notifier(self, user_id: UUID, notifier: NotifierDTO) -> None:
        self._client.set(f"{CacheKeys.NOTIFIER_TELEGRAM}:{user_id}", json.dumps(asdict(notifier)), CacheKeys.THIRTY_DAYS_IN_SECONDS)

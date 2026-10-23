import json
from dataclasses import asdict
from typing import cast
from uuid import UUID

import redis

from ..constants import CacheKeys
from ..dtos import NotifierDTO


class NotifierRepository:

    def __init__(self, client: redis.Redis) -> None:
        self._client = client


    def get_notifier(self, user_id: UUID) -> NotifierDTO:
        notifier = cast(bytes | None, self._client.get(f"{CacheKeys.NOTIFIER_TELEGRAM}:{user_id}"))
        return NotifierDTO(**json.loads(notifier)) if notifier else NotifierDTO()


    def save_notifier(self, user_id: UUID, notifier: NotifierDTO) -> None:
        self._client.set(f"{CacheKeys.NOTIFIER_TELEGRAM}:{user_id}", json.dumps(asdict(notifier)), CacheKeys.THIRTY_DAYS_IN_SECONDS)

from typing import Protocol
from ..dtos import NotifierDTO


class NotifierProtocol(Protocol):

    def get_notifier(self, user_id: str) -> NotifierDTO: ...
    def save_notifier(self, user_id: str, notifier: NotifierDTO): ...

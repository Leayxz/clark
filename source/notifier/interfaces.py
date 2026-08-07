from typing import Protocol
from ..dtos import NotifierDTO


class NotifierProtocol(Protocol):

    def get_notifier(self, email: str) -> NotifierDTO: ...
    def save_notifier(self, email: str, notifier: NotifierDTO): ...

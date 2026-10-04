from .interfaces import NotifierProtocol
from ..dtos import NotifierDTO

class NotifierService:

    def __init__(self, repository: NotifierProtocol) -> None:
        self._repository = repository


    def get_notifier(self, user_id: str) -> NotifierDTO:
        return self._repository.get_notifier(user_id)


    def save_notifier(self, user_id: str, notifier: NotifierDTO):
        return self._repository.save_notifier(user_id, notifier)

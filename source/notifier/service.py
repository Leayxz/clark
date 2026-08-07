from .interfaces import NotifierProtocol
from ..dtos import NotifierDTO

class NotifierService:

    def __init__(self, repository: NotifierProtocol) -> None:
        self._repository = repository


    def get_status_notifier(self, email: str) -> bool:
        notifier = self._repository.get_notifier(email)
        return True if notifier else False


    def get_notifier(self, email: str) -> NotifierDTO:
        return self._repository.get_notifier(email)


    def save_notifier(self, email: str, notifier: NotifierDTO):
        return self._repository.save_notifier(email, notifier)

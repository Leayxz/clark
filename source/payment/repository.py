from .interfaces import PaymentProtocol

class PaymentRepository(PaymentProtocol):

    def get_payment_status(self, email: str) -> bool:
        return False

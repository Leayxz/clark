import qrcode, base64
from io import BytesIO

from .interfaces import PaymentProtocol, ProviderProtocol
from ..dtos import PaymentDTO
from ..constants import CacheKeys


class PaymentService:

    def __init__(self,
                 repository: PaymentProtocol,
                 provider: ProviderProtocol) -> None:

                self._repository = repository
                self._provider = provider


    def validated_payment(self, email) -> bool:
        return self._repository.get_payment_status(email)


    async def generate_qrcode_for_payment_in_sats(self, email: str):
        invoice = await self._provider.create_deposit_in_sats(email, CacheKeys.THIRTY_DAYS_IN_SECONDS)
        qrcode = self._generate_qrcode(invoice.payment_request)
        return PaymentDTO(deposit_id=invoice.deposit_id, payment_request=invoice.payment_request, qrcode=qrcode)


    def _generate_qrcode(self, payment_request: str):
        qrcd = qrcode.make(payment_request)
        buffer = BytesIO()
        qrcd.save(buffer, "PNG")
        qrcd64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return qrcd64


    def generate_qrcode_for_payment_in_pix(self):
        pass

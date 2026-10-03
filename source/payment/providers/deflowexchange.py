import uuid
import requests
from decimal import Decimal
from uuid import UUID

from ..interfaces import DeflowExchangeProtocol
from ...configurations import DeflowExchange
from ...dtos import DeflowExchangeDTO, PaymentDTO
from ...errors import Error
from ...telemetry.tracing import tracer
from ...telemetry.logging import logger


class DeflowExchangeProvider(DeflowExchangeProtocol):

    def create_deposit_pix(self, user_id: UUID, amount: Decimal, payment: PaymentDTO) -> DeflowExchangeDTO | Error:
        # Leia seção Fluxo Create Deposit Pix em /payment/readme.md

        with tracer.start_as_current_span("provider.deflow.create_deposit_pix"):

            try:
                headers = {
                    "Authorization": f"Bearer {DeflowExchange.API_KEY}",
                    "X-DF-Secret": DeflowExchange.API_SECRET,
                    "X-DF-Idempotency-Key": str(uuid.uuid4()),
                    "Content-Type": "application/json",
                }

                if DeflowExchange.API_PASSPHRASE:
                    headers["X-DF-Passphrase"] = DeflowExchange.API_PASSPHRASE

                amount_in_cents = int(amount * 100)

                payload = { "amountInCents": amount_in_cents, "payerTaxNumber": payment.payer_tax_number, }

                response = requests.post(
                    url=f"{DeflowExchange.API_URL}/deposit/create",
                    headers=headers,
                    json=payload,
                    timeout=30,
                )

                print(response.json())

                if response.status_code >= 400:
                    error_message = response.json().get("message", "Erro desconhecido no provedor de pagamento.")
                    logger.error("❌ Falha ao criar PIX", extra={"user_id": str(user_id), "error": error_message}, exc_info=True)
                    if "CPF" in error_message or "CNPJ" in error_message:
                        return Error.INVALID_TAX_NUMBER
                    elif "depósito recente" in error_message or "Aguarde" in error_message:
                        return Error.DUPLICATE_DEPOSIT
                    return Error.DEFLOW_ERROR

                data = response.json()
                deposit_data = data["data"]

                logger.info("💾 PIX criado", extra={"user_id": str(user_id), "payment_id": deposit_data["id"], "coupon_code": payment.coupon_code})

                return DeflowExchangeDTO(
                    payment_id=deposit_data["id"],
                    qr_code=deposit_data["qrCopyPaste"],
                    amount_brl=amount,
                    status=deposit_data["status"],
                    expires_at=deposit_data.get("expiresAt"),
                )

            except Exception as e:
                logger.error("❌ Erro inesperado no provedor PIX", extra={"user_id": str(user_id), "error": str(e)}, exc_info=True)
                return Error.DEFLOW_ERROR

    def check_payment_status(self, payment_id: str) -> str | Error:

        with tracer.start_as_current_span("provider.deflow.check_payment_status"):
            try:
                headers = {
                    "Authorization": f"Bearer {DeflowExchange.API_KEY}",
                    "X-DF-Secret": DeflowExchange.API_SECRET,
                }

                if DeflowExchange.API_PASSPHRASE:
                    headers["X-DF-Passphrase"] = DeflowExchange.API_PASSPHRASE

                response = requests.get(
                    url=f"{DeflowExchange.API_URL}/deposit-status/{payment_id}",
                    headers=headers,
                    timeout=30,
                )

                if response.status_code >= 400:
                    error_message = response.json().get("message", "Erro desconhecido.")
                    logger.error("❌ Falha ao verificar status", extra={"payment_id": payment_id, "error": error_message}, exc_info=True)
                    return Error.DEFLOW_ERROR

                data = response.json()
                logger.info("💊 Status verificado", extra={"payment_id": payment_id, "status": data["data"]["status"]})
                return data["data"]["status"]

            except Exception as e:
                logger.error("❌ Erro inesperado na verificação de status", extra={"payment_id": payment_id, "error": str(e)}, exc_info=True)
                return Error.DEFLOW_ERROR
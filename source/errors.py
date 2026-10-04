from rest_framework import status
from enum import Enum

class Error(Enum):
    USER_NOT_FOUND = "Usuário não encontrado."
    INVALID_CREDENTIALS = "Credenciais inválidas."
    INVALID_COUPON = "Cupom inválido."
    USER_ALREADY_EXISTS = "Usuário já cadastrado."
    TOO_MANY_REQUESTS = "Muitas requisições. Tente após 60 segundos."
    NOT_FOUND = "Não encontrado."
    AUTOMATION_ALREADY_RUNNING = "Desligue a automação antes de salvar novas configurações."
    BTC_PRICE_UNAVAILABLE = "Cotação BTC/BRL indisponível. Tente novamente."
    AFFILIATE_NOT_FOUND = "Afiliado não encontrado."
    AFFILIATE_ALREADY_EXISTS = "Afiliado já cadastrado."
    COUPON_ALREADY_EXISTS = "Cupom já em uso."
    LIQUID_ADDRESS_EXISTS = "Endereço Liquid já cadastrado."
    INVALID_INPUT = "Dados inválidos."
    PROVIDER_ERROR = "Erro interno do provedor."
    INVALID_TAX_NUMBER = "CPF/CNPJ inválido."
    DUPLICATE_DEPOSIT = "Depósito recente. Aguarde."
    DEFLOW_ERROR = "Erro no provedor de pagamento."


ERROR_CODE_MAPPING = {
    Error.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    Error.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    Error.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
    Error.INVALID_COUPON: status.HTTP_400_BAD_REQUEST,
    Error.TOO_MANY_REQUESTS: status.HTTP_429_TOO_MANY_REQUESTS,

    Error.AUTOMATION_ALREADY_RUNNING: status.HTTP_409_CONFLICT,
    Error.USER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    Error.BTC_PRICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    Error.AFFILIATE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    Error.AFFILIATE_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    Error.COUPON_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    Error.LIQUID_ADDRESS_EXISTS: status.HTTP_409_CONFLICT,
    Error.PROVIDER_ERROR: status.HTTP_503_SERVICE_UNAVAILABLE,
    Error.INVALID_TAX_NUMBER: status.HTTP_400_BAD_REQUEST,
    Error.DUPLICATE_DEPOSIT: status.HTTP_409_CONFLICT,
    Error.DEFLOW_ERROR: status.HTTP_502_BAD_GATEWAY,
}

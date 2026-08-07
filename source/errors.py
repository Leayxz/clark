from rest_framework import status
from enum import Enum

class Error(Enum):
    USER_NOT_FOUND = "Usuário não encontrado."
    INVALID_CREDENTIALS = "Credenciais inválidas."
    USER_ALREADY_EXISTS = "Usuário já cadastrado."
    TOO_MANY_REQUESTS = "Muitas requisições. Tente após 60 segundos."
    NOT_FOUND = "Não encontrado."
    AUTOMATION_ALREADY_RUNNING = "Desligue a automação antes de salvar novas configurações."


ERROR_CODE_MAPPING = {
    Error.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    Error.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    Error.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
    Error.TOO_MANY_REQUESTS: status.HTTP_429_TOO_MANY_REQUESTS,

    Error.AUTOMATION_ALREADY_RUNNING: status.HTTP_409_CONFLICT,
    Error.USER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
}

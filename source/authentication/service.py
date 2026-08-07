import bcrypt
from jose import jwt, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from .interfaces import AuthenticationProtocol
from .dtos import AuthResult
from ..errors import Error
from ..configurations import Authentication


class AuthService:

    def __init__(self, repository: AuthenticationProtocol) -> None:
        self._repository = repository


    def register(self, email: str, password: str) -> AuthResult:
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        cadastrado = self._repository.get_user(email=email)
        if cadastrado: return AuthResult(error=Error.USER_ALREADY_EXISTS)
        # faz o cadastro do usuário em banco de dados, inserindo em tabela
        self._repository.save_user(email=email, hashed_password=hashed_password)
        # deve retornar sucesso para o endpoint
        return AuthResult(error=None)


    def authenticate(self, email: str, password: str) -> AuthResult:
        user = self._repository.get_user(email=email)
        if not user: return AuthResult(error=Error.USER_NOT_FOUND)

        if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
            return AuthResult(error=Error.INVALID_CREDENTIALS)

        # deve chamar auditoria depois de autenticar
        access_token, refresh_token = self._generate_tokens(user.email)
        return AuthResult(access_token=access_token, refresh_token=refresh_token)


    def authorize(self, access_token: str, refresh_token: str) -> AuthResult:
        
        try:
            payload = jwt.decode(access_token, Authentication.AUTHORIZATION_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "access": return AuthResult(error=Error.INVALID_CREDENTIALS)
            return AuthResult(subject=payload.get("sub"))

        except ExpiredSignatureError:

            try:
                # tenta utilizar o refresh_token para autenticar o usuário, se falhar, retorna erro e o usuário deve fazer login
                payload = jwt.decode(refresh_token, Authentication.AUTHORIZATION_SECRET_KEY, algorithms=["HS256"])
                if payload.get("type") != "refresh": return AuthResult(error=Error.INVALID_CREDENTIALS)
            
            except ExpiredSignatureError:
                return AuthResult(error=Error.INVALID_CREDENTIALS)
            
            # gera novos access e refresh tokens para o usuário continuar na aplicação sem precisar fazer login
            new_access_token, new_refresh_token = self._generate_tokens(payload["sub"])
            return AuthResult(subject=payload.get("sub"), new_access_token=new_access_token, new_refresh_token=new_refresh_token)

        except Exception:
            return AuthResult(error=Error.INVALID_CREDENTIALS)


    def _generate_tokens(self, subject: str) -> tuple[str, str]:
        access_expiracao = datetime.now(timezone.utc) + timedelta(minutes=10)
        access_payload = {"sub": subject, "type": "access", "exp": access_expiracao}
        access_token = jwt.encode(access_payload, Authentication.AUTHORIZATION_SECRET_KEY, algorithm="HS256")

        refresh_expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)
        refresh_payload = {"sub": subject, "type": "refresh", "exp": refresh_expiracao}
        refresh_token = jwt.encode(refresh_payload, Authentication.AUTHORIZATION_SECRET_KEY, algorithm="HS256")

        return access_token, refresh_token

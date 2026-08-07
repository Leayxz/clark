from .interfaces import AuthenticationProtocol
from .models import User


class AuthenticationRepository(AuthenticationProtocol):

    def get_user(self, email: str):
        """Retorna um usuário cadastrado ou None utilizando o email como busca."""
        return User.objects.filter(email=email).first()


    def save_user(self, email: str, hashed_password: bytes):
        """Insere um usuário no banco de dados."""
        User.objects.create(email=email, hashed_password=hashed_password.decode("utf-8"))
        return

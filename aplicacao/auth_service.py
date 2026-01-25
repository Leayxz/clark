from aplicacao.DTOs import AuthServiceResponse
from django.contrib.auth import authenticate

class AuthService:

      @staticmethod
      def autenticar_usuario(email, senha) -> AuthServiceResponse:
            usuario = authenticate(username = email, password = senha)
            if not usuario: return AuthServiceResponse(msg = "⚠️ Email ou senha incorretos.", code = 401, data = None)
            return AuthServiceResponse(msg = None, code = 200, data = usuario)

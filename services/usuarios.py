from typing import Any, Optional
from web.forms import CadastroForm
from django.contrib.auth import authenticate
from dataclasses import dataclass
from django.core.cache import cache
from infra.index import log_sys, log_user
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

@dataclass
class UserServiceResult:
      sucesso: bool
      code: Optional[int]
      msg: Optional[str]
      data: Optional[Any] = None

class Usuario:

      def __init__(self, dados: CadastroForm, user):
            self._dados = dados
            self._username = user.username

      async def cadastrar_novo_usuario(self):

            # 1. Cadastra novo usuário e explode até o middleware em caso de erro.
            await sync_to_async(User.objects.create_user)(username=self._dados.email, password=self._dados.senha) # Debt: preciso verificar email já existente mesmo que o model garanta isso. E criar interface. E resolver pylance

            # 2. Novo usuário cadastrado no sistema.
            log_sys().info(f"✅ Novo usuário cadastrado com sucesso.")
            return UserServiceResult(sucesso=True, code=200, msg=f"✅ Novo usuário cadastrado com sucesso.")

      async def autenticar_usuario(self) -> UserServiceResult:

            # 1. Valida autenticação ou retorna erro
            user = await sync_to_async(authenticate)(username=self._dados.email, password=self._dados.senha) # Isso é IO? Deveria ser Async?

            # 2. Usuário não autenticado retorna erro ao client sem gravar log.
            if not user: return UserServiceResult(sucesso=False, code=401, msg="⚠️ Email ou senha incorretos.")

            # 3. Usuário autenticado Grava log e retorna sucesso.
            log_user(self._username).info(f"✅ Usuário autenticado com sucesso.")
            return UserServiceResult(sucesso=True, code=200, msg=f"✅ Usuário autenticado com sucesso.", data=user)

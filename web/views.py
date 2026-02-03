from dataclasses import asdict
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from infra.pagamentos import validar_pagamento
from infra.index import log_user, log_sys
from aplicacao.task import rodar_automacao
from aplicacao.services.auth import AuthService
from aplicacao.services.usuarios_service import Usuarios
from aplicacao.services.dashboard import DashboardService
from aplicacao.services.qrcode import GerarQrCode

def login_user(request):


      if request.method == "GET":
            return render(request, "login.html")

      if request.method == "POST":

            email = request.POST.get("email"); senha = request.POST.get("senha")

            # VALIDA USUARIO, ABRE SESSAO E GRAVA LOGS
            resposta = AuthService().autenticar_usuario(email, senha)
            login(request, resposta.data)
            log_user(request.user.username).info(f"✅ Usuário Autenticado/Logado")
            return redirect("/pagina_inicial/")

      return redirect("/login_user/")

def cadastro_user(request):

      if request.method == "GET":
            return render(request, "cadastro.html")

      if request.method == "POST":

            # VALIDACAO INPUT
            email = request.POST.get('email'); senha = request.POST.get('senha')
            if not email or not senha: return render(request, "cadastro.html", {"erro": "Email e senha são obrigatórios."})

            # SERVICE PARA CADASTRAR NOVO USUARIO
            Usuarios().cadastrar_novo_usuario(email, senha) # TRATAR EXCEPTIONS NO MIDDLEWARE COM CONTEXTO
            log_sys().info(f"✨ Novo Usuário Cadastrado")
            return redirect("login_user")

      return redirect("/cadastro_user/")

@login_required()
def logout_user(request):

      email = request.user.username
      logout(request)
      log_user(email).info(f"🔒 Log Out.")
      return redirect('login_user')

@login_required()
def pagina_inicial(request):

      user = request.user

      if request.method == 'GET':
            resposta = DashboardService(user).inicializar_dashboard()
            return render(request, "pagina_inicial.html", asdict(resposta)) # asdict() ENVIA O DTO COMPLETO COMO CHAVE:VALOR

      if request.method == 'POST':
            resposta = GerarQrCode(user).gerar_qrcode()
            return JsonResponse(asdict(resposta), status = resposta.code)

      return redirect("/pagina_inicial/")

@login_required
def config_automacao(request):

      username = request.user.username
      logger_user = log_user(username)
      logger_sys = log_sys()
      config = cache.get(f"CONFIGS_USER_{username}")

      if request.method == "GET":

            # PROTECAO ROTA PARA USUARIOS SEM PAGAMENTO
            pagamento_confirmado = validar_pagamento(request.user)
            if pagamento_confirmado: return render(request, "config_automacao.html", {"config": config, 'id_task': config['id_task']})

            return redirect("/pagina_inicial/")

      if request.method == "POST":

            # SALVA AS CONFIGURAÇOES EM CACHE
            try:
                  config['quantity1'] = int(request.POST.get("quantity1"))
                  config['quantity2'] = int(request.POST.get("quantity2"))
                  config['quantity3'] = int(request.POST.get("quantity3"))
                  config['quantity4'] = int(request.POST.get("quantity4"))

                  config['preco_referencia'] = float(request.POST.get("preco_referencia"))
                  config['comprar_abaixo'] = float(request.POST.get('comprar_abaixo'))

                  config['percentual_lucro'] = float(request.POST.get("percentual_lucro"))
                  config['variacao_compra'] = int(request.POST.get("variacao_compra"))

                  config['limite_margem'] = int(request.POST.get("limite_margem"))
                  config['percentual_seguranca_liquidacao'] = float(request.POST.get("percentual_seguranca_liquidacao"))

                  cache.set(f"CONFIGS_USER_{username}", config, timeout = 30*24*60*60)
                  logger_user.info(f"✅ Novas configurações salvas para automação.")
                  return redirect("/config_automacao/")

            except Exception as error:
                  logger_sys.error(f"❌ Erro ao salvar novas configurações:", exc_info = True)
                  return redirect("/config_automacao/")

      return redirect("/pagina_inicial/")

@login_required
def ligar_desligar_automacao(request):

      username = request.user.username
      logger_user = log_user(username)

      if request.method == "POST":

            # CONFIG AUTOMACAO E DADOS API    
            config = cache.get(f"CONFIGS_USER_{username}")
            dados_api = {"API_KEY": request.POST.get("API_KEY"), "SECRET_KEY": request.POST.get("SECRET_KEY")}

            # SE EXISTIR TASK > DESLIGA REMOVENDO API
            if config['id_task']:
                  config['id_task'] = False
                  cache.set(f"CONFIGS_USER_{username}", config, timeout = 30*24*60*60)
                  cache.delete(f"{username}_CACHE_API:")
                  logger_user.info(f"✅ Task Encerrada e API Apagada.")

            # SE NAO EXISTIR TASK > LIGAR
            else:
                  config['id_task'] = True
                  cache.set(f"CONFIGS_USER_{username}", config, timeout = 30 * 24 * 60 * 60)
                  cache.set(f"{username}_CACHE_API:", dados_api, timeout = 30 * 24 * 60 * 60)
                  rodar_automacao.delay(username)
                  logger_user.info(f"✅ Task Salva e Enviada")

      return redirect("/config_automacao")

@login_required
def salvar_telegram(request):

      username = request.user.username
      logger_user = log_user(username)

      if request.method == 'GET':
            return render(request, "telegram.html")

      if request.method == 'POST':

            TOKEN_TELEGRAM = request.POST.get('TOKEN_TELEGRAM')
            ID_TELEGRAM = request.POST.get('ID_TELEGRAM')

            user_telegram = {'TOKEN_TELEGRAM': TOKEN_TELEGRAM, 'ID_TELEGRAM': ID_TELEGRAM }
            cache.set(f"USER_TELEGRAM_{username}", user_telegram, timeout = 30 * 24 * 60 * 60)

            logger_user.info(f"✅ Telegram Salvo.")
            return redirect('pagina_inicial')

      return redirect("pagina_inicial")

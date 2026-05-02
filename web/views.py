from dataclasses import asdict

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache

from services.task import rodar_automacao
from services.telegram import Telegram
from services.dashboard import Dashboard
from services.qrcode import GerarQrCode
from services.usuarios import Usuario
from services.configuracoes import ConfigAutomacao

from web.forms import AutomacaoForm, CadastroForm, TelegramForm

from infra.pagamentos import Pagamento
from infra.index import log_user, log_sys

async def login_user(request):
      "Renderiza página de login e abre sessão para usuários cadastrados em DB."

      if request.method == "GET":
            return render(request, "login.html")

      if request.method == "POST":

            # 1. Recebe email e senha do client
            dados = CadastroForm(request.POST)

            # 2. Confirma se o usuário está cadastrado
            resposta = await Usuario(dados=dados, user=request.user).autenticar_usuario()
            if resposta.sucesso: return render(request, "login.html", asdict(resposta))

            # 3. Abre sessão e grava log individual por usuário
            login(request, resposta.data)
            log_user(request.user.username).info(f"✅ Usuário Autenticado/Logado")
            return redirect("/pagina_inicial/")

async def cadastro_user(request):
      "Renderiza página de cadastro e cadastra novo usuário."

      if request.method == "GET":
            return render(request, "cadastro.html")

      if request.method == "POST":

            # 1. Recebe email, senha e faz validação básica
            dados = CadastroForm(request.POST)
            dados_automacao = AutomacaoForm(request.POST)
            if not dados.is_valid(): return render(request, "cadastro.html", {"erro": "Email e senha são obrigatórios."})

            # 2. Cadastra novo usuário e configurações padrão para automação do usuário
            await Usuario(dados=dados, user=request.user).cadastrar_novo_usuario() # TRATAR EXCEPTIONS NO MIDDLEWARE COM CONTEXTO?
            # Montar função para configurações padrão para automação do usuário - Aonde? Quem é responsável pelas configurações da automação? Exatamente!
            ConfigAutomacao(username=request.user.username, dados_automacao=dados_automacao)
            log_sys().info(f"✨ Novo Usuário Cadastrado e configurações padrão salvas.")

            return redirect("login_user")

      return redirect("/cadastro_user/")

@login_required()
def logout_user(request):
      dados = CadastroForm(request.POST)
      logout(request)
      log_user(dados.email).info(f"🔒 Log Out.")
      return redirect('login_user')

@login_required() # resolver essa bomba
async def pagina_inicial(request):

      if request.method == 'GET':

            # 1. Informações necessárias para o dashboard do usuário
            dados_automacao = ConfigAutomacao(cache, log_user).buscar_configuracoes(username=request.user.username)
            dados_telegram = Telegram(cache, log_user).buscar_telegram(username=request.user.username)

            resposta = await Dashboard(dados_automacao=dados_automacao, dados_telegram=dados_telegram, user=request.user).inicializar_dashboard()
            return render(request, "pagina_inicial.html", asdict(resposta)) # asdict() envia o DTO/OBJ completo com todos os dados

      if request.method == 'POST':
            resposta = GerarQrCode(request.user).gerar_qrcode()
            return JsonResponse(asdict(resposta), status=resposta.code)

      return redirect("/pagina_inicial/")

@login_required() # Arrumar um jeito de corrigir isso.
async def config_automacao(request):

      if request.method == "GET":

            # 1. Validação de pagamento antes de liberar a página de configuração
            pagamento = await Pagamento(request.user).validar_invoice()
            if not pagamento.sucesso: return redirect("/pagina_inicial/")

            # 2. Compartilhando configurações da automação salvas para o HTML
            configuracoes = ConfigAutomacao(username=request.user.username).buscar_configuracoes()

            return render(request, "config_automacao.html", {"config": configuracoes})

      if request.method == "POST":

            # 1. 
            dados = AutomacaoForm(request.POST) # Validação dos dados através do Django Forms? Valida o que exatamente? - Ainda não sei direito.
            if not dados.is_valid(): return render(request, "config_automacao.html", {"erro": "Erro ao processar dados para novas configurações."})

            # 2. Salva novas configurações para automação em cache
            ConfigAutomacao(dados_automacao=dados, username=request.user.username).salvar_configuracoes()
            return render(request, "/config_automacao/", {"sucesso": "Configurações salvas com sucesso."})

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
      "Exibe HTML do telegram e permite salvamento do número em cache."

      if request.method == 'GET':
            return render(request, "telegram.html")

      if request.method == 'POST':

            dados = TelegramForm(request.POST)
            Telegram(username=request.user.username, dados=dados).salvar_telegram()
            return redirect('pagina_inicial')

      return redirect("pagina_inicial")

import sys
from django.apps import AppConfig

class AplicacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicacao'

    def ready(self):

      # NAO RODA WEBSOCKET NO CELERY
      if 'celery' in sys.argv[0]: return

      # RODA WEBSOCKET APENAS NO SERVIDOR E SOMENTE DEPOIS DE TUDO CONFIGURADO
      from .preco_socket import preco_socket
      preco_socket()

import sys
from django.apps import AppConfig

class InfraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infra'

    def ready(self):

      # NAO RODA WEBSOCKET NO CELERY
      if 'celery' in sys.argv[0]: return

      # RODA WEBSOCKET APENAS NO SERVIDOR E SOMENTE DEPOIS DE TUDO CONFIGURADO
      from infra.preco_socket import preco_socket
      preco_socket()

# IMPEDE QUE O WEBSOCKET RODE NO CELERY, RODANDO APENAS NO SERVIDOR
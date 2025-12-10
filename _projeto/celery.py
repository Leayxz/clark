import os
from celery import Celery

# SETTINGS PADRAO DJANGO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_projeto.settings')

app = Celery('_projeto')

# LE CONFIGURACAO DJANGO COM "CELERY_"
app.config_from_object('django.conf:settings', namespace = 'CELERY')

# AUTO-DISCOVER TASKS.PY
app.autodiscover_tasks()

# ARQUIVO DE CONFIGURACAO DO CELERY
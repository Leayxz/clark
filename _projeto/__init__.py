from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)

# AUTOMATICAMENTE CARREGA O celery.py QUANDO O DJANGO IMPORTAR O _projeto
# SEM ISSO O DJANGO NAO IMPORTA AUTOMATICAMENTE AS CONFIGURACOES DO celery.py

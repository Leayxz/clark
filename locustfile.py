from locust import HttpUser, task, between
from random import randint

class TesteCarga(HttpUser):
      wait_time = between(1, 3)

      def on_start(self):
            self.login()

      def login(self):
            payload = {'email': f'teste{randint(1, 1000)}@hotmail.com', 'senha': '123'}
            self.client.post("/", data = payload, allow_redirects = False)

      @task
      def carga(self):
            self.client.get("/pagina_inicial/")

# Todas as rotas foram testadas, problemas idêntificados e corrigidos.
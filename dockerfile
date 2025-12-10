FROM python:3.13

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# COPIA ARQUIVOS
COPY _projeto _projeto
COPY aplicacao aplicacao
COPY dominio dominio
COPY infra infra
COPY web web

# COPIA ARQUIVOS
COPY manage.py .
COPY deps.txt .

RUN pip install --no-cache-dir -r deps.txt

# IMAGEM DO PROJETO SENDO CONSTRUIDA PELO DOCKER
# SOMENTE O QUE E NECESSARIO SENDO BUILDADO
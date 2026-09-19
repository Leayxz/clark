# Clark

> Execução de estratégias de trading em tempo real para múltiplos usuários simultâneos.

## Engineering Highlights

- **Arquitetura híbrida** — API Django síncrona coexistindo com motor de trading asyncio, comunicados via Redis Pub/Sub
- **Multi-exchange via composição** — Providers (LNMarkets, Hyperliquid, BingX) implementando mesma interface
- **Estado em memória** — Dados quentes no processo async, cache/banco como fallback de recuperação
- **Observabilidade fim-a-fim** — OpenTelemetry SDK → Collector → Grafana/Prometheus/Loki/Tempo
- **Repository Pattern + DI** — Protocols explícitas + container manual
- **CI/CD** → GitHub Actions → GHCR → AWS EC2

## Problema

Operava manualmente em exchanges. Cada segundo de delay era decisão perdida. Construí a primeira versão: função única, estado espalhado em cache. Quando o processo caiu, perdi o estado de todas as ordens.

A queda mostrou três problemas: recuperação de estado após falha, tolerância a queda de processo, desacoplamento entre execução síncrona e assíncrona.

## Decisões Arquiteturais

### Decisão 1: Separar sync de async

Tentei Django REST Framework totalmente async com `sync_to_async`. Gastei dias tentando fazer o event loop do Redis conversar com o ciclo de vida assíncrono. O problema aparece na reconexão: `Event Loop is Closed`.

| Abordagem | Trade-off |
|-----------|-----------|
| Tudo async | Event loop instável com Redis, complexidade alta |
| Híbrido | API síncrona estável, motor async isolado, comunicação via Pub/Sub |

---

### Decisão 2: Repository Pattern + DI

Cada módulo define uma `Protocol`. Implementação injetada via `container.py`.

| Sem | Com |
|-----|-----|
| ORM espalhado nos services | Troca de banco = troca implementação, sem alteração em services |

---

### Decisão 3: Estado em memória

Bater em Redis a cada tick de preço adicionava latência sob carga.

| Abordagem | Trade-off |
|-----------|-----------|
| Redis direto a cada tick | Latência sob carga |
| Memória + fallback | Dados quentes em memória; cache/banco só em restart ou dessincronia |

---

### Decisão 4: Separação por domínio

Primeira versão separava por tipo de arquivo (models, views juntos). Misturava autenticação, trading e pagamento no mesmo escopo.

Reestruturei por responsabilidade: `authentication/`, `automation/`, `payment/`, `notifier/`, `websockets/`, `dashboard/`.

---

### Decisão 5: Multi-exchange via composição

Cada exchange é um provider em `websockets/providers/`. Todos implementam `ExchangeProtocol`.

| Sem | Com |
|-----|-----|
| `if/else` por exchange no orchestrator | Adicionar exchange = criar provider, sem alteração no orquestrador |

Suporte: LNMarkets, Hyperliquid, BingX.

## Funcionalidades

- Cadastro e login (JWT com renovação automática)
- Geração de invoices Lightning Network via QR Code
- Configuração de automação por usuário
- Trading automático: compras/vendas em faixas de preço
- Notificação via Telegram
- Dashboard em tempo real

## Stack

| Camada | Tecnologias |
|--------|-------------|
| API | Python 3.13, Django 5, Django REST Framework |
| Motor async | asyncio, WebSockets, SQLAlchemy, Alembic |
| Mensageria | Redis Pub/Sub |
| Persistência | PostgreSQL, Redis |
| Pagamentos | LNMarkets, Bitcoin Lightning Network |
| Observabilidade | OpenTelemetry, Grafana, Prometheus, Loki, Tempo |
| Deploy | Docker Compose, GitHub Actions, GHCR, AWS EC2 |
| Testes | pytest, pytest-asyncio |

## Serviços

| Serviço | Porta |
|---------|-------|
| nginx | 80, 443 |
| web | — |
| postgresql | 5432 |
| redis | 6379 |
| grafana | 3000 |
| prometheus | 9090 |
| loki | 3100 |
| tempo | 3200 |
| collector | 4317 |

**Total: 9 serviços.**

## Observabilidade

A aplicação instrumenta tracing, logging e metrics via OpenTelemetry SDK. O Collector recebe na porta 4317 e distribui para os backends.

| Tipo | Backend |
|------|---------|
| Traces | Tempo |
| Logs | Loki |
| Métricas | Prometheus |

- Pipeline: `telemetry/collector.yaml`
- Instrumentação: `source/telemetry/`

## Testes

| Ferramenta | Uso |
|------------|-----|
| pytest | Runner |
| pytest-asyncio | Testes do motor assíncrono |
| SQLite in-memory | Banco descartável por fixture |
| AsyncMock | Mock de dependências externas |

Local: `source/websockets/test_repository.py`

## Deploy

| Workflow | Arquivo | Trigger |
|----------|---------|---------|
| CI | `.github/workflows/ci.yml` | Push/PR |
| CD | `.github/workflows/cd.yml` | CI concluído |

CD: build Docker → push GHCR → SSH EC2 → `docker compose down && up -d`.

## Como Executar

```bash
git clone https://github.com/Leayxz/clark.git
cd clark
docker compose up -d
```

| Serviço | URL |
|---------|-----|
| Web | http://localhost |
| Grafana | http://localhost:3000 |

## Estrutura

```
clark/
├── compose.yml
├── telemetry/
├── alembic/
├── config/
├── source/
│   ├── authentication/
│   ├── automation/
│   ├── dashboard/
│   ├── notifier/
│   ├── payment/
│   ├── telemetry/
│   ├── websockets/
│   ├── operations/
│   ├── onboarding/
│   ├── affiliates/
│   ├── web/
│   ├── scripts/
│   ├── container.py
│   └── ...
└── .github/workflows/
```

---

**Leandro R. Martins** — Back-end Python
- GitHub: [Leayxz](https://github.com/Leayxz)
- LinkedIn: [leayx](https://linkedin.com/in/leayx)
- Email: leandromartinsr10@hotmail.com

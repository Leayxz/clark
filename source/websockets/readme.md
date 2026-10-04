# WebSockets Multi-Exchange

### Processos independentes

wslnmarkets.py e wshyperliquid.py são processos independentes — `asyncio.run(main())` separado para cada um. Estado em memória (`_all_running_credentials`, `_all_running_open_orders`, etc.) é local a cada processo. Não compartilham memória entre si. Mesmo user_id em duas exchanges simultâneas não colide: cada uma tem seu repositório isolado.

### Tabelas compartilhadas

O user_id é salvo como String(36) com UUID formatado, exemplo: 01a01a22-8c4c-71a6-ab57-f15d7b23faa2. Django e SQLAlchemy compartilham a mesma tabela mas serializam UUID de forma diferente, Django `UUIDField` usa `CHAR(36)`, SQLAlchemy `UUID(as_uuid=True)` usa `BLOB`, por isso usamos `String(36)` e `CharField(36)` para compatibilidade. Quando migrarmos para PostgreSQL usamos `UUID` nativo e esse conflito deixa de existir.

### Motivo do Pub/Sub

O processo websocket precisa saber em tempo real quais automações foram ativadas ou desativadas pelo Django, sem fazer polling de Redis a cada tick de preço, justamente porque o canal `automation` (pubsub) entrega esses eventos (`automation_started`, `automation_stopped`) via push. O estado inicial ainda carrega do Redis SET `all_activated_automation` via `synchronize_websocket()`, carregando os usuários já ativos na memória local, enquanto mudanças subsequentes chegam apenas como eventos pubsub, mantendo a lista `_all_activated_automations` atualizada sem I/O em cada price update. A alternativa seria fazer `SMEMBERS` no Redis a cada tick, o que adiciona latência desnecessária no hot path, quando o pubsub notifica instantaneamente apenas quem realmente precisa saber.

### Dono do schema de closed_orders

A tabela closed_orders pertence ao Alembic, não ao Django. O model Django correspondente (source/dashboard/models.py) declara `managed = False` justamente por isso: o Django lê e escreve nessa tabela, mas não gerencia o schema dela. Toda alteração de coluna, tipo ou restrição passa por uma revisão em alembic/versions/.

Isso foi quebrado uma vez e custou dados. O Django tinha as migrações 0002 e 0003 do app dashboard, escritas sobre um model desatualizado, que no SQLite usam `_remake_table` (CREATE new__closed_orders, INSERT SELECT, DROP, RENAME). Ao rodarem, recriaram a tabela apenas com as três colunas que o model Django conhecia na época (order_id, profit, closed_at), derrubando user_id e total_fees, e preenchendo closed_at com a string literal 'created_at' vinda do auto_now_add. O Alembic já estava em head, então nada restaurou as colunas. As linhas foram recuperadas das páginas livres do SQLite e repovoadas pela revisão cb156c57f308.

Regra: o Django não gera migrações para closed_orders. Se o model Django precisar mudar, a mudança é feita no model SQLAlchemy e a migração correspondente é criada no Alembic. O banco do projeto é o sqlite.db da raiz, apontado por caminho absoluto em source/websockets/container.py para não depender do diretório de execução.

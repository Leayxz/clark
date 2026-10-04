# Automação

Este módulo expõe a API que o front da página de estratégia consome: configuração da
estratégia, credenciais da exchange e o liga/desliga da automação.

## Chaves no Redis

A configuração e as credenciais vivem em **hashes por exchange**, e são compartilhadas com
o websocket, que é quem de fato opera. A chave sempre carrega a exchange, porque o mesmo
usuário pode ter uma estratégia diferente em cada uma:

```
automation_configuration:{exchange}:{user_id}   hash
automation_credentials:{exchange}:{user_id}     hash
```

O websocket lê esses mesmos hashes, então qualquer escrita daqui precisa manter o formato.

## Propriedade dos campos

O hash de configuração é dividido entre os dois lados:

| Campo | Dono | Observação |
|---|---|---|
| `marginUSD`, `leverage`, `percentage_profit`, `buy_variation` | formulário | o usuário edita na página |
| `wallet_balance`, `last_buy_up`, `last_buy_down` | websocket | saldo e referências de compra, atualizados a cada operação |

O `hset` só sobrescreve os campos que recebe, então salvar a configuração grava apenas os
quatro do formulário e deixa os do websocket intactos. Gravar os sete zeraria o saldo e as
referências.

## `percentage_profit`

O hash guarda o valor em pontos percentuais (`"0.50"`). O websocket divide por 100 ao ler,
porque a fórmula de alvo de preço trabalha com a fração (`0.005`). A página lê o valor
bruto, que é o que o campo de porcentagem deve exibir.

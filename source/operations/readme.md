# Calculadora de contrato inverso

### O que é

A calculadora responde quanto rende uma operação de contrato inverso BTC/USD, contrato inverso quer dizer que a quantidade é cotada em dólar mas a margem e o lucro são pagos em sats, então quanto maior o preço do BTC menos sats vale o mesmo dólar, e é essa inversão que confunde no começo, o código fica em source/scripts/operations.ts e o HTML em source/operations/templates/operations.html, nunca edite o static/javascript/operations.js direto porque ele é saída de compilação e o tsc sobrescreve.

### O erro que existia antes

O bloco antigo perguntava quanto você precisava para fazer X sats e devolvia o número rotulado como margem em USD, só que por dentro o cálculo partia da quantidade, e quantidade e margem são coisas diferentes, a quantidade é o notional em dólar que a LNMarkets chama de Quantidade, a margem é a quantidade dividida pela alavancagem, a 5x os dois diferem por cinco vezes, então o rótulo dizia uma coisa e a conta fazia outra, além disso a meta era dividida por um campo de número de operações que não existia no HTML e caía num default de 100, o que fazia o resultado aparecer dividido por cem sem avisar ninguém, era por isso que seis sats viravam uma margem de zero dólar, e ainda havia dois blocos separados com preços padrão diferentes, 90000 e 90700 num e 86000 e 86700 no outro, então a mesma pergunta dava duas respostas dependendo de onde você olhava.

### Vocabulário

quantidade é o valor em dólar da posição, no print da LNMarkets é o campo Quantidade.
margem é a quantidade dividida pela alavancagem, é o que precisa estar na conta, no print é o campo Margem Negociação e aparece em sats.
sats por USD é quanto de lucro cada dólar de quantidade gera, e depende só dos preços de entrada e saída, nunca do tamanho da posição.
P/L bruto é o lucro antes das taxas, P/L líquido é depois, a LNMarkets mostra o bruto no campo P/L.

### A conta

Tudo cabe numa equação só:

```
total_sats = quantidade_usd × sats_por_usd × operações
```

onde:

```
sats_por_usd = 100_000_000 × |1/entrada - 1/saída|
```

A margem sai de:

```
margem_sats = quantidade_usd × 100_000_000 / entrada / alavancagem
margem_usd  = margem_sats / 100_000_000 × entrada
```

e margem_usd é a mesma coisa que quantidade_usd dividido pela alavancagem, as duas formas dão o mesmo número, use a que for mais fácil de ler no momento.

O P/L bruto por ordem sai de:

```
pl_bruto = quantidade_usd × 100_000_000 × (1/entrada - 1/saída)
```

e a taxa de cada lado é floor(tamanho_em_sats × taxa), com taxa padrão de 0,1% por lado, a LNMarkets trunca pra baixo, não arredonda pra cima, por isso o floor é obrigatório e não um detalhe.

### As duas perguntas

O usuário só precisa de duas perguntas e elas são a mesma equação resolvida para variáveis diferentes, o botão Tenho X USD responde "se eu colocar X dólares de quantidade por ordem, quantos sats eu faço", o botão Quero X sats responde "se eu quiser X sats no total, quantos dólares eu preciso por ordem", quando você troca de modo o valor do campo é convertido em vez de zerado, então dá pra ir e voltar sem perder o cenário, a liquidação é 1 dividido por (1/entrada mais margem_em_btc dividido pela quantidade) e devolve null quando o denominador é zero ou negativo, que é o caso do short que não tem preço de liquidação.

### Exemplo

Com entrada em 90000, saída em 90700, alavancagem 5x e 100 operações, um dólar de quantidade rende 8 sats brutos por ordem, o que dá 6 sats líquidos depois de 2 sats de taxa, e isso pede 222 sats de margem, ou 0,20 dólar, se você subir pra 19 dólares de quantidade o P/L bruto vai pra 162 sats por ordem e a margem pra 4222 sats, o que dá 3,80 dólares, e 19 dólares em 100 operações fecham 16200 sats, a conta inversa devolve o mesmo, 16200 sats em 100 operações pedem 18,90 dólares de quantidade por ordem.

### Como conferir

Os números abaixo batem com a calculadora da LNMarkets e servem de referência pra regressão, se algum deles mudar a conta quebrou:

| quantidade | entrada | saída | alavancagem | margem | P/L bruto | taxa abertura | taxa fechamento | liquidação |
|---|---|---|---|---|---|---|---|---|
| 1 USD | 90000 | 90700 | 5x | 222 sats | 8 | 1 | 1 | 75.012,5 |
| 19 USD | 90000 | 90700 | 5x | 4222 sats | 162 | 21 | 20 | 75.000,7 |
| 1870 USD | 90000 | 90700 | 5x | 415.555 sats | 16.035 | 2.077 | 2.061 | 75.000,0 |

### Build

Depois de mexer no operations.ts rode npx tsc, depois uv run python manage.py collectstatic --noinput, e confirme com uv run python manage.py check.

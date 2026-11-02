.venv/bin/python __main__.py

Os valores das movimentações são lidos e processados em centavos como inteiros
`int32`. Valores com mais de duas casas decimais são arredondados para o
centavo mais próximo usando arredondamento comercial (`ROUND_HALF_UP`). A
conversão para reais ocorre somente na visualização do gráfico.

## Pipeline

O SQLite em `data/database/financial.db` é a fonte de verdade. Os CSVs são organizados por instituição e produto em
`data/input/sources/<instituição>/<produto>/`. Eles são importados de forma
idempotente e o gráfico é gerado em
`data/output/graphs/`. Consultas e relatórios tabulares devem ser feitos
diretamente no SQLite.

O comando `report` gera estes gráficos:

```text
data/output/graphs/values_by_month.png
data/output/graphs/monthly_cashflow.png
data/output/graphs/expenses_by_product.png
data/output/graphs/expenses_by_category.png
data/output/graphs/transaction_activity.png
```

Eles mostram, respectivamente, resultado líquido mensal, receitas versus
despesas, despesas por conta/cartão, despesas por categoria e quantidade de
despesas por mês e produto. No gráfico de fluxo mensal, pagamentos da fatura
aparecem em roxo como uma movimentação relacionada ao cartão, separada das
despesas reais para evitar dupla contagem.

```bash
.venv/bin/python __main__.py pipeline
.venv/bin/python __main__.py import
.venv/bin/python __main__.py report
.venv/bin/python -m unittest discover -s tests
```

Cada transação é identificada por `source` e `id`. Os arquivos já importados
são controlados por hash na tabela `imports`; repetir o comando não duplica
registros.

Exemplo de entrada:

```text
data/input/sources/nubank/account/*.csv
data/input/sources/nubank/credit/*.csv
```

Os CSVs de `account` usam o formato de extrato da conta. Os CSVs de `credit`
usam as colunas `date`, `title` e `amount`; os valores do cartão são
interpretados como despesas e armazenados como centavos negativos. Pagamentos
recebidos da fatura são reconhecidos como transferências internas e ignorados
dos indicadores para evitar contar a mesma movimentação duas vezes.

Na conta, lançamentos `Pagamento de fatura` são identificados como pagamentos
do cartão, marcados como transferências internas e exibidos separadamente no
gráfico de fluxo mensal.

Aplicações e resgates RDB representam entradas e saídas do cofrinho do
Nubank. Eles são removidos durante a importação e não são salvos no SQLite,
pois não representam receitas ou despesas reais.

## Arquitetura

O código é organizado em camadas:

```text
app/
├── domain/          regras financeiras e classificação
├── application/     casos de uso do sistema
├── infrastructure/  CSV, SQLite, relatórios e gráficos
└── presentation/    CLI e composição das dependências
```

O fluxo principal é:

```text
CLI
  -> caso de uso de importação
    -> leitor CSV
    -> regras de classificação
    -> repositório SQLite

CLI
  -> caso de uso de relatórios
    -> repositório SQLite
    -> gerador de gráfico
```

As regras de negócio não dependem de `argparse`, SQLite ou matplotlib. Isso
permite trocar a interface por uma API ou dashboard sem reescrever o domínio.
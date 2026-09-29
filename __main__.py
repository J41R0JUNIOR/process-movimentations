from read import read_csv, read_json
from process import Processador
from strategies.agrupar_transacoes_strategy import AgruparTransacoesStrategy
from write import write_json
from pathlib import Path

PASTA_ENTRADA = Path("./data/entrada")
PASTA_SAIDA = Path("./data/saida")
ARQUIVO_DADOS = PASTA_SAIDA / "transacoes.json"
ARQUIVO_AGRUPADO = PASTA_SAIDA / "transacoes_agrupadas.json"


def main():
    todas_transacoes = []

    for arquivo in PASTA_ENTRADA.glob("*.csv"):
        print(f"Lendo: {arquivo.name}")

        transacoes = read_csv(arquivo)
        todas_transacoes.extend(transacoes)

    write_json(ARQUIVO_DADOS, todas_transacoes)
    print(f"\nDados brutos salvos em: {ARQUIVO_DADOS}")

    transacoes_salvas = read_json(ARQUIVO_DADOS)
    processador = Processador()
    processador.add_strategy(AgruparTransacoesStrategy(campo_agrupamento="descricao"))
    resultados = processador.execute_all(transacoes_salvas)
    transacoes_agrupadas = resultados["agrupar_transacoes"]
    write_json(ARQUIVO_AGRUPADO, transacoes_agrupadas)

    print(f"Transações agrupadas salvas em: {ARQUIVO_AGRUPADO}")
    print(f"Total de transações: {len(todas_transacoes)}")
    print(f"Total de grupos: {len(transacoes_agrupadas)}")


if __name__ == "__main__":
    main()
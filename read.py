import csv
import json
from pathlib import Path
from typing import Any


def read_csv(caminho: Path) -> list[dict[str, Any]]:
    transacoes: list[dict[str, Any]] = []

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            transacao = {
                "data": linha["Data"],
                "valor": float(linha["Valor"]),
                "identificador": linha["Identificador"],
                "descricao": linha["Descrição"],
            }

            transacoes.append(transacao)

    return transacoes


def read_json(caminho: Path) -> list[dict[str, Any]]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)
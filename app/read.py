import csv
import json
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transaction = {
                "date": row["Data"],
                "value": float(row["Valor"]),
                "id": row["Identificador"],
                "description": row["Descrição"],
            }

            transactions.append(transaction)

    return transactions


def read_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
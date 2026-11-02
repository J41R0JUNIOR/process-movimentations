import csv
import hashlib
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any
from datetime import datetime

INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1


def _parse_cents(value: str, path: Path, row_number: int) -> int:
    try:
        amount = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cents_int = int(amount * 100)
    except InvalidOperation as error:
        raise ValueError(
            f"Invalid monetary value at {path}:{row_number}: {value!r}"
        ) from error

    if not INT32_MIN <= cents_int <= INT32_MAX:
        raise ValueError(
            f"Monetary value out of int32 range at {path}:{row_number}: {value!r}"
        )

    return cents_int


def _parse_date(value: str, path: Path, row_number: int) -> str:
    try:
        return datetime.strptime(value, "%d/%m/%Y").date().isoformat()
    except ValueError as error:
        raise ValueError(
            f"Invalid date at {path}:{row_number}: {value!r}"
        ) from error


def read_csv(path: Path) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            transaction = {
                "date": _parse_date(row["Data"], path, row_number),
                "value": _parse_cents(row["Valor"], path, row_number),
                "id": row["Identificador"],
                "description": row["Descrição"],
                "source": "nubank",
                "source_file": path.name,
            }

            transactions.append(transaction)

    return transactions


def read_credit_csv(path: Path) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            date = row["date"]
            title = row["title"]
            raw_amount = row["amount"].replace(" ", "").replace(".", "")
            amount = _parse_cents(
                raw_amount.replace(",", "."),
                path,
                row_number,
            )
            transaction_id = hashlib.sha256(
                f"{path.name}:{row_number}:{date}:{title}:{amount}".encode()
            ).hexdigest()
            transactions.append(
                {
                    "date": date,
                    "value": -amount if amount >= 0 else abs(amount),
                    "id": transaction_id,
                    "description": title,
                    "source": "nubank",
                    "product": "credit",
                    "source_file": path.name,
                }
            )

    return transactions
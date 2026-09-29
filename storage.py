from pathlib import Path

from configuration import Configuration
from process import Transaction
from read import read_csv, read_json
from write import write_json


def load_transactions() -> list[Transaction]:
    transactions: list[Transaction] = []

    for file in Path(Configuration.INPUT_FOLDER.value).glob("*.csv"):
        print(f"Reading: {file.name}")
        transactions.extend(read_csv(file))

    return transactions


def save_raw_transactions(transactions: list[Transaction]) -> None:
    path = Path(Configuration.RAW_DATA_FILE.value)
    write_json(path, transactions)
    print(f"\nRaw data saved to: {path}")


def load_saved_transactions() -> list[Transaction]:
    return read_json(Path(Configuration.RAW_DATA_FILE.value))

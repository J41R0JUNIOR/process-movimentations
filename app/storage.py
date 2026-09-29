from pathlib import Path

import pandas as pd

from app.configuration import Configuration
from app.process import Transaction
from app.read import read_csv, read_json
from app.write import write_json


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


def load_saved_transactions() -> pd.DataFrame:
    return pd.read_json(
        Path(Configuration.RAW_DATA_FILE.value),
        convert_dates=False,
    )

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.configuration import CleanupConfiguration
from app.write import write_json


@dataclass(frozen=True)
class CleanTransactionsStrategy:
    """Remove internal Nubank savings-account movements."""

    name: str = CleanupConfiguration.CLEAN_TRANSACTIONS.value

    def execute(self, transactions: pd.DataFrame) -> pd.DataFrame:
        excluded_descriptions = {
            CleanupConfiguration.SAVINGS_APPLICATION.value,
            CleanupConfiguration.SAVINGS_REDEMPTION.value,
        }
        cleaned_transactions = transactions[
            ~transactions["description"].isin(excluded_descriptions)
        ].copy()
        path = Path(CleanupConfiguration.CLEANED_DATA_FILE.value)
        write_json(
            path,
            cleaned_transactions.to_dict(orient="records"),
        )
        print(f"Cleaned transactions saved to: {path}")
        return cleaned_transactions

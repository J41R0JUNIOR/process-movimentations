from dataclasses import dataclass
from pathlib import Path

from configuration import CleanupConfiguration
from process import Transaction
from write import write_json


@dataclass(frozen=True)
class CleanTransactionsStrategy:
    """Remove internal Nubank savings-account movements."""

    name: str = CleanupConfiguration.CLEAN_TRANSACTIONS.value

    def execute(self, transactions: list[Transaction]) -> list[Transaction]:
        cleaned_transactions = [
            transaction
            for transaction in transactions
            if transaction["description"]
            not in {
                CleanupConfiguration.SAVINGS_APPLICATION.value,
                CleanupConfiguration.SAVINGS_REDEMPTION.value,
            }
        ]
        path = Path(CleanupConfiguration.CLEANED_DATA_FILE.value)
        write_json(path, cleaned_transactions)
        print(f"Cleaned transactions saved to: {path}")
        return cleaned_transactions

from dataclasses import dataclass
from pathlib import Path
from matplotlib.pylab import Enum
import pandas as pd
from app.configuration import FILES
from app.write import write_json


@dataclass(frozen=True)
class CleanTransactionsStrategy:
    """Remove internal Nubank savings-account movements."""
 
    def execute(self, transactions: pd.DataFrame) -> pd.DataFrame:
        excluded_descriptions = {
            CleanUp.SAVINGS_APPLICATION.value,
            CleanUp.SAVINGS_REDEMPTION.value,
        }
        cleaned_transactions = transactions[
            ~transactions["description"].isin(excluded_descriptions)
        ].copy()
        path = Path(FILES.CLEANED_DATA_FILE.value)
        write_json(
            path,
            cleaned_transactions.to_dict(orient="records"),
        )
        print(f"Cleaned transactions saved to: {path}")
        return cleaned_transactions

class CleanUp(str, Enum):
    SAVINGS_APPLICATION = "Aplicação RDB"
    SAVINGS_REDEMPTION = "Resgate RDB"

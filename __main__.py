from app.configuration import NAMES
from app.process import Processor
from app.strategies.clean_transactions_strategy import CleanTransactionsStrategy
from app.strategies.values_by_month_strategy import ValuesByMonthStrategy
from app.storage import (
	load_saved_transactions,
	load_transactions,
	save_raw_transactions,
)

def main():
    all_transactions = load_transactions()
    save_raw_transactions(all_transactions)
    saved_transactions = load_saved_transactions()

    cleaned_transactions = CleanTransactionsStrategy().execute(saved_transactions)

    processor = Processor(
        ValuesByMonthStrategy(should_generate_chart=True),
    )

    processor.execute_all(cleaned_transactions)



if __name__ == "__main__":
    main()
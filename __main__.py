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

    results = processor.execute_all(cleaned_transactions)

    values_by_month = results[NAMES.VALUES_BY_MONTH.value]

    print(f"Total transactions: {len(all_transactions)}")
    print(f"Total values by month: {len(values_by_month)}")


if __name__ == "__main__":
    main()
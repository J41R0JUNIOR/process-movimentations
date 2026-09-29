from configuration import Configuration
from process import Processor
from strategies.clean_transactions_strategy import CleanTransactionsStrategy
from strategies.group_transactions_strategy import GroupTransactionsStrategy
from strategies.values_by_month_strategy import ValuesByMonthStrategy
from storage import (
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
        GroupTransactionsStrategy(),
        ValuesByMonthStrategy(should_generate_chart=True),
    )

    results = processor.execute_all(cleaned_transactions)

    grouped_transactions = results[Configuration.GROUP_TRANSACTIONS.value]
    values_by_month = results[Configuration.VALUES_BY_MONTH.value]

    print(f"Total transactions: {len(all_transactions)}")
    print(f"Total groups: {len(grouped_transactions)}")
    print(f"Total values by month: {len(values_by_month)}")


if __name__ == "__main__":
    main()
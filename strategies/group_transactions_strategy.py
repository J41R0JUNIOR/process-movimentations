from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from configuration import Configuration
from process import Transaction
from write import write_json


@dataclass(frozen=True)
class GroupTransactionsStrategy:
	"""Group transactions by a field and sum their values."""

	grouping_field: str = Configuration.GROUPING_FIELD.value
	name: str = Configuration.GROUP_TRANSACTIONS.value

	def execute(self, transactions: list[Transaction]) -> list[Transaction]:
		groups: defaultdict[str, dict[str, Any]] = defaultdict(
			lambda: {"quantity": 0, "value": Decimal("0")}
		)

		for transaction in transactions:
			key = str(transaction.get(self.grouping_field, "")).strip()
			group = groups[key]
			group["quantity"] += 1
			group["value"] += Decimal(str(transaction.get("value", 0)))

		result = [
			{
				self.grouping_field: key,
				"quantity": group["quantity"],
				"value": float(group["value"]),
			}
			for key, group in sorted(groups.items())
		]
		path = Path(Configuration.GROUPED_TRANSACTIONS_FILE.value)
		write_json(path, result)
		print(f"Grouped transactions saved to: {path}")
		return result
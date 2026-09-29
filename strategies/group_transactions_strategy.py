from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from configuration import Configuration
from process import Transaction
from write import write_json


@dataclass(frozen=True)
class GroupTransactionsStrategy:
	"""Group transactions by a field and sum their values."""

	grouping_field: str = Configuration.GROUPING_FIELD.value
	should_generate_chart: bool = False
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
		if self.should_generate_chart:
			self.generate_chart(result)

		return result

	def generate_chart(self, grouped_transactions: list[Transaction]) -> None:
		chart_file = Path(Configuration.GROUPED_CHART_FILE.value)
		chart_file.parent.mkdir(parents=True, exist_ok=True)

		ordered_transactions = sorted(
			grouped_transactions,
			key=lambda transaction: float(transaction["value"]),
		)
		labels = [
			self._shorten_label(str(transaction[self.grouping_field]))
			for transaction in ordered_transactions
		]
		values = [float(transaction["value"]) for transaction in ordered_transactions]
		colors = ["#2e8b57" if value >= 0 else "#c94c4c" for value in values]
		figure, axis = plt.subplots(
			figsize=(12, max(6, len(labels) * 0.35))
		)
		axis.barh(labels, values, color=colors)
		axis.axvline(0, color="#333333", linewidth=0.8)
		axis.set_title("Values grouped by description")
		axis.set_xlabel("Value")
		axis.set_ylabel("Description")
		figure.tight_layout()
		figure.savefig(chart_file, dpi=150)
		plt.close(figure)

	def _shorten_label(self, label: str, max_length: int = 70) -> str:
		if len(label) <= max_length:
			return label
		return f"{label[:max_length - 3]}..."
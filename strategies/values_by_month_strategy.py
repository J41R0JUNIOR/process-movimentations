from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt

from configuration import Configuration
from process import Transaction
from write import write_json


@dataclass(frozen=True)
class ValuesByMonthStrategy:
	"""Sum transaction values by month and generate a chart."""

	should_generate_chart: bool = False
	name: str = Configuration.VALUES_BY_MONTH.value

	def execute(self, transactions: list[Transaction]) -> list[Transaction]:
		totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))

		for transaction in transactions:
			date = datetime.strptime(str(transaction["date"]), "%d/%m/%Y")
			month = date.strftime("%Y-%m")
			totals[month] += Decimal(str(transaction.get("value", 0)))

		result = [
			{"month": month, "value": float(value)}
			for month, value in sorted(totals.items())
		]
		path = Path(Configuration.MONTHLY_VALUES_FILE.value)
		write_json(path, result)
		print(f"Monthly values saved to: {path}")
		if self.should_generate_chart:
			self.generate_chart(result)

		return result

	def generate_chart(self, monthly_values: list[Transaction]) -> None:
		chart_file = Path(Configuration.MONTHLY_CHART_FILE.value)
		chart_file.parent.mkdir(parents=True, exist_ok=True)

		months = [str(item["month"]) for item in monthly_values]
		values = [float(item["value"]) for item in monthly_values]
		figure, axis = plt.subplots(figsize=(10, 5))
		axis.bar(months, values, color="#1769aa")
		axis.axhline(0, color="#333333", linewidth=0.8)
		axis.set_title("Values moved by month")
		axis.set_xlabel("Month")
		axis.set_ylabel("Value")
		axis.tick_params(axis="x", rotation=45)
		figure.tight_layout()
		figure.savefig(chart_file, dpi=150)
		plt.close(figure)
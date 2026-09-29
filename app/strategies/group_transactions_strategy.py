from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.configuration import Configuration
from app.write import write_json


@dataclass(frozen=True)
class GroupTransactionsStrategy:
	"""Group transactions by a field and sum their values."""

	grouping_field: str = Configuration.GROUPING_FIELD.value
	should_generate_chart: bool = False
	name: str = Configuration.GROUP_TRANSACTIONS.value

	def execute(self, transactions: pd.DataFrame) -> pd.DataFrame:
		result = (
			transactions.groupby(self.grouping_field, as_index=False)
			.agg(quantity=("value", "size"), value=("value", "sum"))
			.sort_values(self.grouping_field)
			.reset_index(drop=True)
		)
		path = Path(Configuration.GROUPED_TRANSACTIONS_FILE.value)
		write_json(path, result.to_dict(orient="records"))
		print(f"Grouped transactions saved to: {path}")
		if self.should_generate_chart:
			self.generate_chart(result)

		return result

	def generate_chart(self, grouped_transactions: pd.DataFrame) -> None:
		chart_file = Path(Configuration.GROUPED_CHART_FILE.value)
		chart_file.parent.mkdir(parents=True, exist_ok=True)

		ordered_transactions = grouped_transactions.sort_values("value")
		labels = [self._shorten_label(str(label)) for label in ordered_transactions[self.grouping_field]]
		values = ordered_transactions["value"].astype(float).tolist()
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
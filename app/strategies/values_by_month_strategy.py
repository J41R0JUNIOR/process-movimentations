from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.configuration import FILES, NAMES
from app.write import write_json


@dataclass(frozen=True)
class ValuesByMonthStrategy:
	"""Sum transaction values by month and generate a chart."""

	should_generate_chart: bool = False
	name: str = NAMES.VALUES_BY_MONTH.value

	def execute(self, transactions: pd.DataFrame) -> pd.DataFrame:
		result = (
			transactions.assign(
				month=pd.to_datetime(
					transactions["date"], format="%d/%m/%Y"
				).dt.strftime("%Y-%m")
			)
			.groupby("month", as_index=False)["value"]
			.sum()
			.sort_values("month")
			.reset_index(drop=True)
		)
		path = Path(FILES.VALUES_BY_MONTH_FILE.value)
		write_json(path, result.to_dict(orient="records"))
		print(f"Monthly values saved to: {path}")
		if self.should_generate_chart:
			self.generate_charts(result)

		return result

	def generate_charts(self, monthly_values: pd.DataFrame) -> None:
		months = monthly_values["month"].astype(str).tolist()
		values = monthly_values["value"].astype(float).tolist()
		self._generate_bar_chart(months, values)

	def _generate_bar_chart(self, months: list[str], values: list[float]) -> None:
		chart_file = Path(FILES.MONTHLY_CHART_FILE.value)
		chart_file.parent.mkdir(parents=True, exist_ok=True)
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
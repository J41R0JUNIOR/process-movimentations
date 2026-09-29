from __future__ import annotations
from typing import Any, Protocol

Transaction = dict[str, Any]

class Strategy(Protocol):
	def execute(self, transactions: Any) -> Any:
		...

class Processor:
	def __init__(self, *strategies: Strategy):
		self.strategies = list(strategies)

	def add_strategy(self, strategy: Strategy) -> None:
		self.strategies.append(strategy)

	def execute_all(self, transactions: Any) -> dict[str, Any]:
		results = {}

		for strategy in self.strategies:
			name = getattr(strategy, "name", strategy.__class__.__name__)
			results[name] = strategy.execute(transactions)

		return results

	def execute(self, transactions: Any) -> Any:
		if len(self.strategies) != 1:
			raise ValueError("execute() requires exactly one Strategy; use execute_all()")

		return self.strategies[0].execute(transactions)
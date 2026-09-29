from __future__ import annotations
from typing import Any, Protocol

Transacao = dict[str, Any]

class Strategy(Protocol):
	def execute(self, transacoes: list[Transacao]) -> Any:
		...

class Processador:
	def __init__(self, *strategies: Strategy):
		self.strategies = list(strategies)

	def add_strategy(self, strategy: Strategy) -> None:
		self.strategies.append(strategy)

	def execute_all(self, transacoes_centrais: list[Transacao]) -> dict[str, Any]:
		resultados = {}

		for strategy in self.strategies:
			nome = getattr(strategy, "nome", strategy.__class__.__name__)
			resultados[nome] = strategy.execute(transacoes_centrais)

		return resultados

	def execute(self, transacoes_centrais: list[Transacao]) -> Any:
		if len(self.strategies) != 1:
			raise ValueError("execute() exige exatamente uma Strategy; use execute_all()")

		return self.strategies[0].execute(transacoes_centrais)
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from process import Transacao


@dataclass(frozen=True)
class AgruparTransacoesStrategy:
	"""Agrupa transacoes por um campo e soma seus valores."""

	campo_agrupamento: str = "descricao"
	nome: str = "agrupar_transacoes"

	def execute(self, transacoes: list[Transacao]) -> list[Transacao]:
		grupos: defaultdict[str, dict[str, Any]] = defaultdict(
			lambda: {"quantidade": 0, "valor": Decimal("0")}
		)

		for transacao in transacoes:
			chave = str(transacao.get(self.campo_agrupamento, "")).strip()
			grupo = grupos[chave]
			grupo["quantidade"] += 1
			grupo["valor"] += Decimal(str(transacao.get("valor", 0)))

		return [
			{
				self.campo_agrupamento: chave,
				"quantidade": grupo["quantidade"],
				"valor": float(grupo["valor"]),
			}
			for chave, grupo in sorted(grupos.items())
		]
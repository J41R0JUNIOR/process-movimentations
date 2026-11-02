from dataclasses import dataclass


@dataclass(frozen=True)
class Classification:
    transaction_type: str
    category: str
    is_internal: bool = False
    is_ignored: bool = False
    ignore_reason: str | None = None


def classify(description: str, amount_cents: int) -> Classification:
    normalized = description.casefold()

    if "aplicação rdb" in normalized:
        return Classification(
            "investment",
            "cofrinho",
            is_internal=True,
            is_ignored=True,
            ignore_reason="Aplicação no cofrinho",
        )
    if "resgate rdb" in normalized:
        return Classification(
            "investment",
            "cofrinho",
            is_internal=True,
            is_ignored=True,
            ignore_reason="Resgate do cofrinho",
        )
    if "transferência de saldo" in normalized:
        return Classification("transfer", "transferências", is_internal=True)
    if "pagamento recebido" in normalized:
        return Classification(
            "transfer",
            "transferências",
            is_internal=True,
            is_ignored=True,
            ignore_reason="Pagamento de fatura",
        )
    if "taxa" in normalized or "juros" in normalized:
        return Classification("expense", "taxas")
    for keyword, category in (
        ("ifood", "alimentação"),
        ("restaurante", "alimentação"),
        ("mercado", "alimentação"),
        ("uber", "transporte"),
        ("combustível", "transporte"),
        ("farmácia", "saúde"),
        ("hospital", "saúde"),
        ("aluguel", "moradia"),
        ("netflix", "lazer"),
        ("spotify", "lazer"),
        ("amazon", "compras"),
    ):
        if keyword in normalized:
            return Classification("expense", category)
    if amount_cents >= 0:
        return Classification("income", "não classificado")
    return Classification("expense", "não classificado")

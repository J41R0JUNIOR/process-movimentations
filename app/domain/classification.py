from dataclasses import dataclass


@dataclass(frozen=True)
class Classification:
    transaction_type: str
    category: str
    is_internal: bool = False
    is_ignored: bool = False
    ignore_reason: str | None = None
    is_card_payment: bool = False


def is_savings_movement(description: str) -> bool:
    normalized = description.casefold()
    return "aplicação rdb" in normalized or "resgate rdb" in normalized


def classify(description: str, amount_cents: int) -> Classification:
    normalized = description.casefold()

    if "transferência de saldo" in normalized:
        return Classification("transfer", "transferências", is_internal=True)
    if "pagamento recebido" in normalized:
        return Classification(
            "transfer",
            "transferências",
            is_internal=True,
            is_ignored=True,
            ignore_reason="Pagamento de fatura",
            is_card_payment=True,
        )
    if "pagamento de fatura" in normalized:
        return Classification(
            "transfer",
            "pagamento de cartão",
            is_internal=True,
            is_ignored=True,
            ignore_reason="Pagamento da fatura do cartão",
            is_card_payment=True,
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
        ("steam", "jogos"),
    ):
        if keyword in normalized:
            return Classification("expense", category)
    if amount_cents >= 0:
        return Classification("income", "não classificado")
    return Classification("expense", "não classificado")

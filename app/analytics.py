import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt

from app.domain.merchant import is_installment, normalize_merchant


def _save_chart(figure: plt.Figure, chart_path: Path) -> None:
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)


def monthly_summary(connection: sqlite3.Connection) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT substr(date, 1, 7) AS month,
               COALESCE(SUM(CASE WHEN transaction_type = 'income'
                                 AND is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS income_cents,
               COALESCE(SUM(CASE WHEN transaction_type = 'expense'
                                 AND is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS expense_cents,
               COALESCE(SUM(CASE WHEN transaction_type = 'transfer'
                                 AND is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS transfer_cents,
               COALESCE(SUM(CASE WHEN transaction_type = 'investment'
                                 AND is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS investment_cents,
               COALESCE(SUM(CASE WHEN is_card_payment = 1 AND amount_cents < 0
                                 THEN -amount_cents ELSE 0 END), 0)
                   AS card_payment_cents,
               COALESCE(SUM(CASE WHEN is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS net_cents
        FROM transactions
        GROUP BY month
        ORDER BY month
        """
    )
    return [dict(row) for row in rows]


def monthly_product_expenses(
    connection: sqlite3.Connection,
) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT substr(date, 1, 7) AS month, product,
               SUM(-amount_cents) AS expense_cents
        FROM transactions
        WHERE transaction_type = 'expense' AND is_ignored = 0
        GROUP BY month, product
        ORDER BY month, product
        """
    )
    return [dict(row) for row in rows]


def category_summary(connection: sqlite3.Connection) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT category, COUNT(*) AS transaction_count,
               SUM(amount_cents) AS total_cents
        FROM transactions
        WHERE transaction_type = 'expense' AND is_ignored = 0
        GROUP BY category
        ORDER BY total_cents
        """
    )
    return [dict(row) for row in rows]


def transaction_activity(
    connection: sqlite3.Connection,
) -> list[dict[str, int | str | float]]:
    rows = connection.execute(
        """
        SELECT substr(date, 1, 7) AS month, product,
               COUNT(*) AS transaction_count,
               SUM(-amount_cents) AS expense_cents,
               AVG(-amount_cents) AS average_expense_cents
        FROM transactions
        WHERE transaction_type = 'expense' AND is_ignored = 0
        GROUP BY month, product
        ORDER BY month, product
        """
    )
    return [dict(row) for row in rows]


def weekday_expenses(
    connection: sqlite3.Connection,
) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT strftime('%w', date) AS weekday_number, product,
               COUNT(*) AS transaction_count,
               SUM(-amount_cents) AS expense_cents
        FROM transactions
        WHERE transaction_type = 'expense' AND is_ignored = 0
        GROUP BY weekday_number, product
        ORDER BY weekday_number, product
        """
    )
    return [dict(row) for row in rows]


def weekday_average_expenses(
    connection: sqlite3.Connection,
) -> list[dict[str, int | str | float]]:
    rows = connection.execute(
        """
        SELECT strftime('%w', date) AS weekday_number, product,
               COUNT(*) AS transaction_count,
               AVG(-amount_cents) AS average_expense_cents
        FROM transactions
        WHERE transaction_type = 'expense' AND is_ignored = 0
        GROUP BY weekday_number, product
        ORDER BY weekday_number, product
        """
    )
    return [dict(row) for row in rows]


def recurring_expenses(
    connection: sqlite3.Connection,
    months_window: int = 6,
) -> list[dict[str, int | str | float]]:
    if months_window < 1:
        raise ValueError("months_window must be at least 1")

    rows = connection.execute(
        """
        SELECT date, product, description, amount_cents
        FROM transactions
        WHERE transaction_type = 'expense'
          AND is_ignored = 0
          AND product = 'credit'
          AND lower(description) NOT LIKE '%pix%'
        ORDER BY date
        """
    )
    transactions = list(rows)
    available_months = sorted(
        {row["date"][:7] for row in transactions},
        reverse=True,
    )
    recent_months = set(available_months[:months_window])

    grouped: dict[tuple[str, str], list[sqlite3.Row]] = {}
    for row in transactions:
        if row["date"][:7] not in recent_months:
            continue
        if is_installment(row["description"]):
            continue
        merchant = normalize_merchant(row["description"])
        if merchant:
            grouped.setdefault((row["product"], merchant), []).append(row)

    recurring = []
    for (product, merchant), transactions in grouped.items():
        months = {row["date"][:7] for row in transactions}
        if len(months) < 3:
            continue
        total_cents = sum(-int(row["amount_cents"]) for row in transactions)
        recurring.append(
            {
                "product": product,
                "merchant": merchant,
                "occurrences": len(transactions),
                "months": len(months),
                "total_cents": total_cents,
                "average_cents": total_cents / len(transactions),
            }
        )
    return sorted(recurring, key=lambda row: int(row["total_cents"]), reverse=True)


def generate_monthly_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    summary = monthly_summary(connection)
    months = [str(row["month"]) for row in summary]
    values = [int(row["net_cents"]) / 100 for row in summary]
    figure, axis = plt.subplots(figsize=(10, 5))
    colors = ["#d32f2f" if value < 0 else "#1769aa" for value in values]
    axis.bar(months, values, color=colors)
    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.set_title("Monthly net movement")
    axis.set_xlabel("Month")
    axis.set_ylabel("Value (BRL)")
    axis.tick_params(axis="x", rotation=45)
    _save_chart(figure, chart_path)


def generate_cashflow_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    summary = monthly_summary(connection)
    months = [str(row["month"]) for row in summary]
    income = [int(row["income_cents"]) / 100 for row in summary]
    expenses = [-int(row["expense_cents"]) / 100 for row in summary]
    card_payments = [int(row["card_payment_cents"]) / 100 for row in summary]
    figure, axis = plt.subplots(figsize=(10, 5))
    positions = list(range(len(months)))
    width = 0.25
    axis.bar(
        [position - width for position in positions],
        income,
        width,
        label="Income",
        color="#1f77b4",
    )
    axis.bar(
        positions,
        expenses,
        width,
        label="Expenses",
        color="#d32f2f",
    )
    axis.bar(
        [position + width for position in positions],
        card_payments,
        width,
        label="Card payment",
        color="#7b1fa2",
    )
    axis.set_xticks(list(positions), months, rotation=45)
    axis.set_ylabel("Value (BRL)")
    axis.set_title("Monthly income and expenses")
    axis.legend()
    _save_chart(figure, chart_path)


def generate_product_expenses_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = monthly_product_expenses(connection)
    months = sorted({str(row["month"]) for row in rows})
    products = sorted({str(row["product"]) for row in rows})
    figure, axis = plt.subplots(figsize=(10, 5))
    positions = list(range(len(months)))
    width = 0.8 / max(len(products), 1)
    for index, product in enumerate(products):
        values = [
            next(
                (
                    int(row["expense_cents"]) / 100
                    for row in rows
                    if row["month"] == month and row["product"] == product
                ),
                0,
            )
            for month in months
        ]
        axis.bar(
            [position - 0.4 + width * (index + 0.5) for position in positions],
            values,
            width,
            label=product,
        )
    axis.set_xticks(positions, months, rotation=45)
    axis.set_ylabel("Expenses (BRL)")
    axis.set_title("Expenses by product")
    axis.legend()
    _save_chart(figure, chart_path)


def generate_category_expenses_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = category_summary(connection)
    categories = [str(row["category"]) for row in rows]
    values = [-int(row["total_cents"]) / 100 for row in rows]
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.barh(categories, values, color="#1769aa")
    axis.set_xlabel("Expenses (BRL)")
    axis.set_title("Expenses by category")
    _save_chart(figure, chart_path)


def generate_activity_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = transaction_activity(connection)
    months = sorted({str(row["month"]) for row in rows})
    products = sorted({str(row["product"]) for row in rows})
    figure, axis = plt.subplots(figsize=(10, 5))
    positions = list(range(len(months)))
    width = 0.8 / max(len(products), 1)
    for index, product in enumerate(products):
        values = [
            next(
                (
                    int(row["transaction_count"])
                    for row in rows
                    if row["month"] == month and row["product"] == product
                ),
                0,
            )
            for month in months
        ]
        axis.bar(
            [position - 0.4 + width * (index + 0.5) for position in positions],
            values,
            width,
            label=product,
        )
    axis.set_xticks(positions, months, rotation=45)
    axis.set_ylabel("Transactions")
    axis.set_title("Expense activity")
    axis.legend()
    _save_chart(figure, chart_path)


def generate_weekday_expenses_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = weekday_expenses(connection)
    weekday_names = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    products = sorted({str(row["product"]) for row in rows})
    positions = list(range(len(weekday_names)))
    width = 0.8 / max(len(products), 1)
    figure, axis = plt.subplots(figsize=(10, 5))
    for index, product in enumerate(products):
        values = [
            next(
                (
                    int(row["expense_cents"]) / 100
                    for row in rows
                    if int(row["weekday_number"]) == (position + 1) % 7
                    and row["product"] == product
                ),
                0,
            )
            for position in positions
        ]
        axis.bar(
            [position - 0.4 + width * (index + 0.5) for position in positions],
            values,
            width,
            label=product,
        )
    axis.set_xticks(positions, weekday_names, rotation=30, ha="right")
    axis.set_ylabel("Expenses (BRL)")
    axis.set_title("Expenses by weekday")
    axis.legend()
    _save_chart(figure, chart_path)


def generate_weekday_average_expenses_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = weekday_average_expenses(connection)
    weekday_names = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    products = sorted({str(row["product"]) for row in rows})
    positions = list(range(len(weekday_names)))
    width = 0.8 / max(len(products), 1)
    figure, axis = plt.subplots(figsize=(10, 5))
    for index, product in enumerate(products):
        values = [
            next(
                (
                    float(row["average_expense_cents"]) / 100
                    for row in rows
                    if int(row["weekday_number"]) == (position + 1) % 7
                    and row["product"] == product
                ),
                0,
            )
            for position in positions
        ]
        axis.bar(
            [position - 0.4 + width * (index + 0.5) for position in positions],
            values,
            width,
            label=product,
        )
    axis.set_xticks(positions, weekday_names, rotation=30, ha="right")
    axis.set_ylabel("Average expense (BRL)")
    axis.set_title("Average expense by weekday")
    axis.legend()
    _save_chart(figure, chart_path)


def generate_recurring_expenses_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    rows = recurring_expenses(connection)[:15]
    labels = [f"{row['merchant']} ({row['product']})" for row in rows]
    values = [float(row["average_cents"]) / 100 for row in rows]
    figure, axis = plt.subplots(figsize=(12, 8))
    axis.barh(labels[::-1], values[::-1], color="#00897b")
    axis.set_xlabel("Average expense per occurrence (BRL)")
    axis.set_title("Recurring expenses")
    axis.tick_params(axis="y", labelsize=8)
    _save_chart(figure, chart_path)

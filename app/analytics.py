import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt


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

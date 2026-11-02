import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt

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
               COALESCE(SUM(CASE WHEN is_ignored = 0 THEN amount_cents ELSE 0 END), 0)
                   AS net_cents
        FROM transactions
        GROUP BY month
        ORDER BY month
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


def generate_monthly_chart(
    connection: sqlite3.Connection,
    chart_path: Path,
) -> None:
    summary = monthly_summary(connection)
    months = [str(row["month"]) for row in summary]
    values = [int(row["net_cents"]) / 100 for row in summary]
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 5))
    colors = ["#d32f2f" if value < 0 else "#1769aa" for value in values]
    axis.bar(months, values, color=colors)
    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.set_title("Monthly net movement")
    axis.set_xlabel("Month")
    axis.set_ylabel("Value (BRL)")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)

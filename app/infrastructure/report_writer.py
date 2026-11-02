import sqlite3
from pathlib import Path

from app.analytics import (
    generate_activity_chart,
    generate_cashflow_chart,
    generate_category_expenses_chart,
    generate_monthly_chart,
    generate_product_expenses_chart,
    generate_weekday_average_expenses_chart,
    generate_weekday_expenses_chart,
)


class ReportWriter:
    def write(
        self,
        connection: sqlite3.Connection,
        chart_paths: dict[str, Path],
    ) -> None:
        generate_monthly_chart(connection, chart_paths["monthly"])
        generate_cashflow_chart(connection, chart_paths["cashflow"])
        generate_product_expenses_chart(connection, chart_paths["product"])
        generate_category_expenses_chart(connection, chart_paths["category"])
        generate_activity_chart(connection, chart_paths["activity"])
        generate_weekday_expenses_chart(connection, chart_paths["weekday"])
        generate_weekday_average_expenses_chart(
            connection,
            chart_paths["weekday_average"],
        )

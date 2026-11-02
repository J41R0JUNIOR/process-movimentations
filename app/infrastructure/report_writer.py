import sqlite3
from pathlib import Path

from app.analytics import generate_monthly_chart


class ReportWriter:
    def write(
        self,
        connection: sqlite3.Connection,
        chart_path: Path,
    ) -> None:
        generate_monthly_chart(connection, chart_path)

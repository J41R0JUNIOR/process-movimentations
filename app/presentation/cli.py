import argparse
from pathlib import Path

from app.application.services import GenerateReports, ImportTransactions
from app.configuration import FILES, FOLDERS
from app.infrastructure.csv_reader import NubankCsvReader
from app.infrastructure.report_writer import ReportWriter
from app.infrastructure.sqlite_repository import SqliteTransactionRepository


def build_services() -> tuple[ImportTransactions, GenerateReports]:
    repository = SqliteTransactionRepository(Path(FILES.DATABASE_FILE.value))
    return (
        ImportTransactions(
            NubankCsvReader(),
            repository,
            Path(FOLDERS.INPUT_FOLDER.value),
        ),
        GenerateReports(
            repository,
            ReportWriter(),
            Path(FILES.MONTHLY_CHART_FILE.value),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importa, classifica e gera relatórios de movimentações financeiras.",
        epilog=(
            "Exemplos:\n"
            "  %(prog)s                 Executa o pipeline completo.\n"
            "  %(prog)s import          Importa os CSVs em data/input/sources/.\n"
            "  %(prog)s report          Gera os relatórios a partir do SQLite."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("pipeline", "import", "report"),
        default="pipeline",
        help="ação a executar (padrão: pipeline): pipeline, import ou report",
    )
    command = parser.parse_args().command
    importer, reporter = build_services()

    if command in ("pipeline", "import"):
        total, inserted = importer.execute()
        print(f"Transactions read: {total}; inserted into SQLite: {inserted}")
    if command in ("pipeline", "report"):
        chart_path = reporter.execute()
        print(f"Chart generated: {chart_path}")

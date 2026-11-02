from pathlib import Path

from app.domain.classification import classify
from app.infrastructure.csv_reader import NubankCsvReader
from app.infrastructure.report_writer import ReportWriter
from app.infrastructure.sqlite_repository import SqliteTransactionRepository


class ImportTransactions:
    def __init__(
        self,
        reader: NubankCsvReader,
        repository: SqliteTransactionRepository,
        input_folder: Path,
    ) -> None:
        self.reader = reader
        self.repository = repository
        self.input_folder = input_folder

    def execute(self) -> tuple[int, int]:
        transactions = self.reader.read_folder(self.input_folder)
        grouped: dict[str, list[dict]] = {}
        for transaction in transactions:
            grouped.setdefault(transaction["source_file"], []).append(transaction)

        inserted = 0
        for source_file, file_transactions in grouped.items():
            prepared = []
            for transaction in file_transactions:
                result = classify(transaction["description"], transaction["value"])
                prepared.append(
                    {
                        **transaction,
                        "transaction_type": result.transaction_type,
                        "category": result.category,
                        "is_internal": int(result.is_internal),
                        "is_ignored": int(result.is_ignored),
                        "ignore_reason": result.ignore_reason,
                    }
                )
            inserted += self.repository.import_file(
                self.input_folder / source_file,
                prepared,
            )
        return len(transactions), inserted


class GenerateReports:
    def __init__(
        self,
        repository: SqliteTransactionRepository,
        writer: ReportWriter,
        chart_path: Path,
    ) -> None:
        self.repository = repository
        self.writer = writer
        self.chart_path = chart_path

    def execute(self) -> Path:
        connection = self.repository.connect()
        try:
            self.writer.write(
                connection,
                self.chart_path,
            )
        finally:
            connection.close()
        return self.chart_path

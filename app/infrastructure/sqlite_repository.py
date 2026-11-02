import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.database import connect, insert_transactions


class SqliteTransactionRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def import_file(
        self,
        source_file: Path,
        transactions: list[dict],
    ) -> int:
        file_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()
        connection = connect(self.database_path)
        try:
            if connection.execute(
                "SELECT 1 FROM imports WHERE file_hash = ?", (file_hash,)
            ).fetchone():
                return 0

            inserted = insert_transactions(connection, transactions)
            connection.execute(
                """
                INSERT INTO imports (
                    source_file, file_hash, imported_at, row_count,
                    inserted_count, status
                ) VALUES (?, ?, ?, ?, ?, 'success')
                """,
                (
                    source_file.name,
                    file_hash,
                    datetime.now(timezone.utc).isoformat(),
                    len(transactions),
                    inserted,
                ),
            )
            connection.commit()
            return inserted
        finally:
            connection.close()

    def connect(self) -> sqlite3.Connection:
        return connect(self.database_path)
